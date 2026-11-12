import csv
from io import StringIO
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from functools import wraps

from flask import Blueprint, Response, abort, jsonify, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.exc import IntegrityError


PERCENTUAIS = {"manicure": 20, "cabeleireira": 30}
CENTAVO = Decimal("0.01")
FUSO_SALAO = timezone(timedelta(hours=-3))


def proteger_celula_csv(valor):
    texto = str(valor or "")
    if texto.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + texto
    return texto


def formatar_valor_csv(valor):
    return format(Decimal(str(valor)).quantize(CENTAVO), ".2f").replace(".", ",")


def create_repasses_blueprint(db, User, Appointment, AppointmentService):
    class CategoriaRepasse(db.Model):
        __tablename__ = "categorias_repasse"
        __table_args__ = (
            CheckConstraint(
                "categoria IN ('manicure', 'cabeleireira')",
                name="ck_categoria_repasse_valida",
            ),
        )

        profissional_id = db.Column(
            db.Integer,
            db.ForeignKey("usuarios.id", ondelete="CASCADE"),
            primary_key=True,
        )
        categoria = db.Column(db.String(20), nullable=False)

    class RepasseRegistro(db.Model):
        __tablename__ = "repasses_registros"
        __table_args__ = (
            UniqueConstraint(
                "semana_inicio",
                "profissional_id",
                name="uq_registro_repasse_semana_profissional",
            ),
            CheckConstraint(
                "status IN ('pendente', 'pago', 'cancelado')",
                name="ck_registro_repasse_status",
            ),
            CheckConstraint("quantidade_servicos > 0", name="ck_registro_repasse_servicos"),
            CheckConstraint("base_calculo >= 0", name="ck_registro_repasse_base"),
            CheckConstraint("valor_repasse >= 0", name="ck_registro_repasse_valor"),
        )

        id = db.Column(db.Integer, primary_key=True)
        semana_inicio = db.Column(db.Date, nullable=False, index=True)
        semana_fim = db.Column(db.Date, nullable=False)
        profissional_id = db.Column(
            db.Integer,
            db.ForeignKey("usuarios.id", ondelete="RESTRICT"),
            nullable=False,
        )
        quantidade_servicos = db.Column(db.Integer, nullable=False)
        percentual = db.Column(db.Integer, nullable=False)
        base_calculo = db.Column(db.Numeric(10, 2), nullable=False)
        valor_repasse = db.Column(db.Numeric(10, 2), nullable=False)
        status = db.Column(db.String(12), nullable=False, default="pendente")
        pago_em = db.Column(db.DateTime(timezone=True), nullable=True)
        cancelado_em = db.Column(db.DateTime(timezone=True), nullable=True)
        criado_em = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
        atualizado_em = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    blueprint = Blueprint("repasses", __name__, template_folder="templates")

    def somente_proprietaria(view):
        @wraps(view)
        @login_required
        def protegido(*args, **kwargs):
            if current_user.tipo != "proprietario":
                abort(403)
            return view(*args, **kwargs)

        return protegido

    def erro(mensagem, status):
        return jsonify(erro=mensagem), status

    def ler_semana(valor):
        try:
            semana = date.fromisoformat(valor or "")
        except (TypeError, ValueError):
            return None
        return semana if semana.weekday() == 0 else None

    def ler_valor(valor, campo):
        try:
            decimal = Decimal(str(valor))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError(f"'{campo}' deve ser um valor monetário válido.") from None
        if not decimal.is_finite() or decimal < 0 or decimal.as_tuple().exponent < -2:
            raise ValueError(f"'{campo}' deve ser não negativo e ter até duas casas decimais.")
        return decimal.quantize(CENTAVO, rounding=ROUND_HALF_UP)

    def ler_quantidade(valor):
        if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
            raise ValueError("'quantidade_servicos' deve ser um inteiro positivo.")
        return valor

    def obter_lancamentos(semana_inicio):
        semana_fim = semana_inicio + timedelta(days=6)
        inicio_local = datetime.combine(semana_inicio, time.min, tzinfo=FUSO_SALAO)
        inicio_utc = inicio_local.astimezone(timezone.utc)
        fim_utc = (inicio_local + timedelta(days=7)).astimezone(timezone.utc)
        lancamentos = (
            db.session.query(AppointmentService, Appointment, User)
            .join(Appointment, AppointmentService.atendimento_id == Appointment.id)
            .join(User, AppointmentService.profissional_id == User.id)
            .filter(
                Appointment.status == "concluido",
                Appointment.concluido_em.isnot(None),
                Appointment.concluido_em >= inicio_utc,
                Appointment.concluido_em < fim_utc,
            )
            .order_by(Appointment.concluido_em, User.nome, AppointmentService.id)
            .all()
        )
        categorias = {
            item.profissional_id: item.categoria
            for item in CategoriaRepasse.query.all()
        }
        grupos = {}
        sem_categoria = {}

        for item, _atendimento, profissional in lancamentos:
            categoria = categorias.get(profissional.id)
            if categoria not in PERCENTUAIS:
                sem_categoria[profissional.id] = {
                    "profissional_id": profissional.id,
                    "profissional": profissional.nome,
                }
                continue

            base = Decimal(str(item.valor_cobrado)).quantize(CENTAVO, rounding=ROUND_HALF_UP)
            percentual = PERCENTUAIS[categoria]
            valor_repasse = (base * Decimal(percentual) / Decimal(100)).quantize(
                CENTAVO,
                rounding=ROUND_HALF_UP,
            )
            grupo = grupos.setdefault(profissional.id, {
                "profissional_id": profissional.id,
                "profissional": profissional.nome,
                "categoria": categoria,
                "percentual": percentual,
                "quantidade_servicos": 0,
                "base_calculo": Decimal("0.00"),
                "valor_repasse": Decimal("0.00"),
            })
            grupo["quantidade_servicos"] += 1
            grupo["base_calculo"] += base
            grupo["valor_repasse"] += valor_repasse

        return semana_fim, grupos, list(sem_categoria.values())

    def serializar(registro):
        profissional = db.session.get(User, registro.profissional_id)
        return {
            "id": registro.id,
            "semana_inicio": registro.semana_inicio.isoformat(),
            "semana_fim": registro.semana_fim.isoformat(),
            "profissional_id": registro.profissional_id,
            "profissional": profissional.nome,
            "quantidade_servicos": registro.quantidade_servicos,
            "percentual": registro.percentual,
            "base_calculo": float(registro.base_calculo),
            "valor_repasse": float(registro.valor_repasse),
            "status": registro.status,
            "pago_em": registro.pago_em.isoformat() if registro.pago_em else None,
            "cancelado_em": registro.cancelado_em.isoformat() if registro.cancelado_em else None,
        }

    def montar_resposta(semana_inicio):
        semana_fim, _grupos, sem_categoria = obter_lancamentos(semana_inicio)
        registros = (
            RepasseRegistro.query
            .filter_by(semana_inicio=semana_inicio)
            .order_by(RepasseRegistro.id)
            .all()
        )
        itens = [serializar(registro) for registro in registros]
        itens.sort(key=lambda item: (item["profissional"].casefold(), item["id"]))
        pendentes = sum(
            (Decimal(str(item["valor_repasse"])) for item in itens if item["status"] == "pendente"),
            Decimal("0.00"),
        )
        pagos = sum(
            (Decimal(str(item["valor_repasse"])) for item in itens if item["status"] == "pago"),
            Decimal("0.00"),
        )
        cancelados = sum(
            (Decimal(str(item["valor_repasse"])) for item in itens if item["status"] == "cancelado"),
            Decimal("0.00"),
        )
        return {
            "semana_inicio": semana_inicio.isoformat(),
            "semana_fim": semana_fim.isoformat(),
            "total_pendente": float(pendentes),
            "total_pago": float(pagos),
            "total_cancelado": float(cancelados),
            "sem_categoria": sem_categoria,
            "itens": itens,
        }

    def criar_registro(semana_inicio, profissional_id, semana_fim, grupo):
        return RepasseRegistro(
            semana_inicio=semana_inicio,
            semana_fim=semana_fim,
            profissional_id=profissional_id,
            quantidade_servicos=grupo["quantidade_servicos"],
            percentual=grupo["percentual"],
            base_calculo=grupo["base_calculo"],
            valor_repasse=grupo["valor_repasse"],
            status="pendente",
        )

    @blueprint.get("/repasses")
    @somente_proprietaria
    def pagina_repasses():
        return render_template("index.html")

    @blueprint.get("/api/repasses/profissionais")
    @somente_proprietaria
    def listar_profissionais():
        categorias = {item.profissional_id: item.categoria for item in CategoriaRepasse.query.all()}
        profissionais = User.query.filter_by(tipo="profissional").order_by(User.nome).all()
        return jsonify([
            {
                "id": profissional.id,
                "nome": profissional.nome,
                "categoria": categorias.get(profissional.id),
                "percentual": PERCENTUAIS.get(categorias.get(profissional.id)),
            }
            for profissional in profissionais
        ])

    @blueprint.put("/api/repasses/profissionais/<int:profissional_id>/categoria")
    @somente_proprietaria
    def atualizar_categoria(profissional_id):
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or payload.get("categoria") not in PERCENTUAIS:
            return erro("Selecione manicure ou cabeleireira.", 400)
        profissional = db.session.get(User, profissional_id)
        if profissional is None or profissional.tipo != "profissional":
            return erro("Profissional não encontrada.", 404)
        categoria = db.session.get(CategoriaRepasse, profissional_id)
        if categoria is None:
            categoria = CategoriaRepasse(profissional_id=profissional_id)
        categoria.categoria = payload["categoria"]
        db.session.add(categoria)
        db.session.commit()
        return jsonify(
            profissional_id=profissional.id,
            profissional=profissional.nome,
            categoria=categoria.categoria,
            percentual=PERCENTUAIS[categoria.categoria],
        )

    @blueprint.get("/api/repasses")
    @somente_proprietaria
    def listar_repasses():
        semana_inicio = ler_semana(request.args.get("semana_inicio"))
        if semana_inicio is None:
            return erro("Selecione uma segunda-feira para consultar a semana.", 400)
        return jsonify(montar_resposta(semana_inicio))

    @blueprint.get("/api/repasses/relatorio.csv")
    @somente_proprietaria
    def exportar_relatorio_csv():
        semana_inicio = ler_semana(request.args.get("semana_inicio"))
        if semana_inicio is None:
            return erro("Selecione uma segunda-feira para exportar o relatório.", 400)
        relatorio = montar_resposta(semana_inicio)
        arquivo = StringIO(newline="")
        escritor = csv.writer(arquivo, delimiter=";", lineterminator="\r\n")
        escritor.writerow([
            "Semana início",
            "Semana fim",
            "Profissional",
            "Serviços",
            "Percentual",
            "Base de cálculo (R$)",
            "Valor do repasse (R$)",
            "Status",
            "Pago em",
            "Cancelado em",
        ])
        rotulos_status = {
            "pendente": "Pendente",
            "pago": "Pago",
            "cancelado": "Cancelado",
        }
        for item in relatorio["itens"]:
            escritor.writerow([
                relatorio["semana_inicio"],
                relatorio["semana_fim"],
                proteger_celula_csv(item["profissional"]),
                item["quantidade_servicos"],
                f'{item["percentual"]}%',
                formatar_valor_csv(item["base_calculo"]),
                formatar_valor_csv(item["valor_repasse"]),
                rotulos_status[item["status"]],
                item["pago_em"] or "",
                item["cancelado_em"] or "",
            ])
        escritor.writerow([])
        escritor.writerow(["Resumo semanal", "Valor (R$)"])
        escritor.writerow(["Total pendente", formatar_valor_csv(relatorio["total_pendente"])])
        escritor.writerow(["Total pago", formatar_valor_csv(relatorio["total_pago"])])
        escritor.writerow(["Total cancelado", formatar_valor_csv(relatorio["total_cancelado"])])

        nome_arquivo = f"relatorio_repasses_{relatorio['semana_inicio']}_{relatorio['semana_fim']}.csv"
        resposta = Response(
            "\ufeff" + arquivo.getvalue(),
            content_type="text/csv; charset=utf-8",
        )
        resposta.headers["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'
        return resposta

    @blueprint.post("/api/repasses")
    @somente_proprietaria
    def criar_repasse():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return erro("Envie um objeto JSON válido.", 400)
        semana_inicio = ler_semana(payload.get("semana_inicio"))
        profissional_id = payload.get("profissional_id")
        if semana_inicio is None:
            return erro("Selecione uma segunda-feira para o repasse.", 400)
        if isinstance(profissional_id, bool) or not isinstance(profissional_id, int) or profissional_id <= 0:
            return erro("Selecione uma profissional válida.", 400)

        semana_fim, grupos, sem_categoria = obter_lancamentos(semana_inicio)
        grupo = grupos.get(profissional_id)
        if grupo is None:
            if any(item["profissional_id"] == profissional_id for item in sem_categoria):
                return erro("Configure a categoria da profissional antes de gerar o repasse.", 400)
            return erro("Não há atendimento concluído para esta profissional nesta semana.", 400)
        existente = RepasseRegistro.query.filter_by(
            semana_inicio=semana_inicio,
            profissional_id=profissional_id,
        ).first()
        if existente is not None:
            return erro("Já existe um registro de repasse para esta profissional nesta semana.", 409)

        registro = criar_registro(semana_inicio, profissional_id, semana_fim, grupo)
        db.session.add(registro)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return erro("Já existe um registro de repasse para esta profissional nesta semana.", 409)
        return jsonify(serializar(registro)), 201

    @blueprint.post("/api/repasses/gerar")
    @somente_proprietaria
    def gerar_repasses():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return erro("Envie um objeto JSON válido.", 400)
        semana_inicio = ler_semana(payload.get("semana_inicio"))
        if semana_inicio is None:
            return erro("Selecione uma segunda-feira para gerar os repasses.", 400)

        semana_fim, grupos, sem_categoria = obter_lancamentos(semana_inicio)
        if not grupos:
            return erro("Não há atendimentos concluídos com categoria configurada nesta semana.", 400)
        existentes = {
            registro.profissional_id
            for registro in RepasseRegistro.query.filter_by(semana_inicio=semana_inicio).all()
        }
        novos = [
            criar_registro(semana_inicio, profissional_id, semana_fim, grupo)
            for profissional_id, grupo in grupos.items()
            if profissional_id not in existentes
        ]
        db.session.add_all(novos)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return erro("Um ou mais repasses foram gerados em outra operação.", 409)
        resposta = montar_resposta(semana_inicio)
        resposta["criados"] = len(novos)
        resposta["sem_categoria"] = sem_categoria
        return jsonify(resposta)

    @blueprint.put("/api/repasses/<int:repasse_id>")
    @somente_proprietaria
    def atualizar_repasse(repasse_id):
        registro = db.session.get(RepasseRegistro, repasse_id)
        if registro is None:
            return erro("Repasse não encontrado.", 404)
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or not payload:
            return erro("Envie os campos que deseja atualizar.", 400)
        campos_permitidos = {
            "semana_inicio", "profissional_id", "quantidade_servicos",
            "base_calculo", "valor_repasse", "status",
        }
        if set(payload) - campos_permitidos:
            return erro("O pedido contém campos não permitidos.", 400)

        try:
            if "semana_inicio" in payload:
                semana_inicio = ler_semana(payload["semana_inicio"])
                if semana_inicio is None:
                    raise ValueError("A semana deve começar em uma segunda-feira.")
                registro.semana_inicio = semana_inicio
                registro.semana_fim = semana_inicio + timedelta(days=6)
            if "profissional_id" in payload:
                profissional_id = payload["profissional_id"]
                profissional = db.session.get(User, profissional_id) if isinstance(profissional_id, int) and not isinstance(profissional_id, bool) else None
                categoria = db.session.get(CategoriaRepasse, profissional_id) if profissional else None
                if profissional is None or profissional.tipo != "profissional" or categoria is None:
                    raise ValueError("Selecione uma profissional com categoria configurada.")
                registro.profissional_id = profissional_id
                registro.percentual = PERCENTUAIS[categoria.categoria]
            if "quantidade_servicos" in payload:
                registro.quantidade_servicos = ler_quantidade(payload["quantidade_servicos"])
            if "base_calculo" in payload:
                registro.base_calculo = ler_valor(payload["base_calculo"], "base_calculo")
            if "valor_repasse" in payload:
                registro.valor_repasse = ler_valor(payload["valor_repasse"], "valor_repasse")
            if "status" in payload:
                if payload["status"] not in {"pendente", "pago"}:
                    raise ValueError("Status deve ser pendente ou pago.")
                registro.status = payload["status"]
                registro.pago_em = datetime.now(timezone.utc) if registro.status == "pago" else None
                registro.cancelado_em = None
        except ValueError as error:
            return erro(str(error), 400)

        registro.atualizado_em = datetime.now(timezone.utc)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return erro("Já existe um repasse para esta profissional nesta semana.", 409)
        return jsonify(serializar(registro))

    @blueprint.delete("/api/repasses/<int:repasse_id>")
    @somente_proprietaria
    def cancelar_repasse(repasse_id):
        registro = db.session.get(RepasseRegistro, repasse_id)
        if registro is None:
            return erro("Repasse não encontrado.", 404)
        if registro.status == "cancelado":
            return erro("Este repasse já foi cancelado.", 409)
        registro.status = "cancelado"
        registro.cancelado_em = datetime.now(timezone.utc)
        registro.atualizado_em = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify(serializar(registro))

    @blueprint.delete("/api/repasses/<int:repasse_id>/definitivo")
    @somente_proprietaria
    def excluir_repasse_definitivamente(repasse_id):
        registro = db.session.get(RepasseRegistro, repasse_id)
        if registro is None:
            return erro("Repasse não encontrado.", 404)
        db.session.delete(registro)
        db.session.commit()
        return "", 204

    @blueprint.post("/api/repasses/pagamentos-lote")
    @somente_proprietaria
    def confirmar_pagamentos_lote():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return erro("Envie um objeto JSON válido.", 400)
        semana_inicio = ler_semana(payload.get("semana_inicio"))
        ids = payload.get("repasses")
        if semana_inicio is None:
            return erro("Selecione uma segunda-feira para fechar a semana.", 400)
        if not isinstance(ids, list) or not ids:
            return erro("Selecione ao menos um repasse.", 400)
        if any(isinstance(item, bool) or not isinstance(item, int) or item <= 0 for item in ids):
            return erro("A lista contém identificadores inválidos.", 400)
        ids = list(dict.fromkeys(ids))
        registros = RepasseRegistro.query.filter(
            RepasseRegistro.semana_inicio == semana_inicio,
            RepasseRegistro.id.in_(ids),
        ).all()
        if len(registros) != len(ids) or any(item.status != "pendente" for item in registros):
            return erro("Há repasse inexistente ou que não está pendente.", 409)

        agora = datetime.now(timezone.utc)
        for registro in registros:
            registro.status = "pago"
            registro.pago_em = agora
            registro.atualizado_em = agora
        db.session.commit()
        return jsonify(montar_resposta(semana_inicio))

    return blueprint, CategoriaRepasse, RepasseRegistro
