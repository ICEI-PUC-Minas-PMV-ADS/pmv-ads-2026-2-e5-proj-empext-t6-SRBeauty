import io
import math
import sqlite3
from collections import Counter
from datetime import date, datetime, time, timedelta
from enum import Enum
from pathlib import Path
from xml.sax.saxutils import escape

from flask import Blueprint, abort, jsonify, render_template, request, send_file
from flask_login import current_user, login_required


BASE_DIR = Path(__file__).resolve().parent
FINANCE_DIR = BASE_DIR / "Financeiro e Relatorios"


class TipoMovimentacao(str, Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"


class FormaPagamento(str, Enum):
    PIX = "pix"
    DINHEIRO = "dinheiro"
    CARTAO_DEBITO = "cartao_debito"
    CARTAO_CREDITO = "cartao_credito"


def create_financeiro_blueprint(db):
    class Movimentacao(db.Model):
        __tablename__ = "movimentacoes"

        id = db.Column(db.Integer, primary_key=True, index=True)
        tipo = db.Column(db.Enum(TipoMovimentacao), nullable=False)
        profissional = db.Column(db.String, default="Salão")
        descricao = db.Column(db.String, nullable=False)
        categoria = db.Column(db.String, nullable=False)
        forma_pagamento = db.Column(db.Enum(FormaPagamento), nullable=False)
        valor_bruto = db.Column(db.Float, nullable=False)
        taxa_cartao = db.Column(db.Float, default=0.0)
        valor_liquido = db.Column(db.Float, nullable=False)
        data = db.Column(db.DateTime, default=datetime.now)

    class FechamentoCaixa(db.Model):
        __tablename__ = "fechamentos_caixa"

        id = db.Column(db.Integer, primary_key=True, index=True)
        data_fechamento = db.Column(db.Date, unique=True, nullable=False)
        total_entradas = db.Column(db.Float, default=0.0)
        total_saidas = db.Column(db.Float, default=0.0)
        total_taxas = db.Column(db.Float, default=0.0)
        saldo_liquido = db.Column(db.Float, default=0.0)
        data_hora_registro = db.Column(db.DateTime, default=datetime.now)

    class ConfiguracaoTaxa(db.Model):
        __tablename__ = "configuracao_taxas"

        forma_pagamento = db.Column(db.Enum(FormaPagamento), primary_key=True)
        percentual = db.Column(db.Float, nullable=False, default=0.0)

    blueprint = Blueprint(
        "financeiro",
        __name__,
        template_folder=str(FINANCE_DIR),
    )

    @blueprint.before_request
    @login_required
    def somente_proprietaria():
        if current_user.tipo != "proprietario":
            abort(403)

    def api_error(message, status=400):
        return jsonify(erro=message), status

    def ler_payload():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            raise ValueError("Envie um objeto JSON válido.")
        return payload

    def ler_percentual(valor):
        try:
            percentual = float(valor)
        except (TypeError, ValueError):
            raise ValueError("O percentual deve ser um número válido.") from None
        if not math.isfinite(percentual):
            raise ValueError("O percentual deve ser um número válido.")
        return max(0.0, percentual)

    def serializar_movimentacao(movimentacao):
        return {
            "id": movimentacao.id,
            "tipo": movimentacao.tipo.value,
            "profissional": movimentacao.profissional or "Salão",
            "descricao": movimentacao.descricao,
            "categoria": movimentacao.categoria,
            "forma_pagamento": movimentacao.forma_pagamento.value,
            "valor_bruto": movimentacao.valor_bruto,
            "taxa_cartao": movimentacao.taxa_cartao or 0.0,
            "valor_liquido": movimentacao.valor_liquido,
            "data": movimentacao.data.isoformat(),
        }

    def serializar_taxa(configuracao):
        return {
            "forma_pagamento": configuracao.forma_pagamento.value,
            "percentual": configuracao.percentual,
        }

    def obter_taxa_percentual(forma_pagamento):
        configuracao = db.session.get(ConfiguracaoTaxa, forma_pagamento)
        return configuracao.percentual if configuracao else 0.0

    def ler_periodo_relatorio():
        hoje = date.today()
        try:
            mes = int(request.args.get("mes", hoje.month))
            ano = int(request.args.get("ano", hoje.year))
        except (TypeError, ValueError):
            raise ValueError("Mês e ano devem ser números válidos.") from None
        if not 1 <= mes <= 12 or not 1 <= ano <= 9999:
            raise ValueError("Informe um mês entre 1 e 12 e um ano válido.")
        inicio = datetime(ano, mes, 1)
        if mes == 12:
            fim = datetime(ano + 1, 1, 1) if ano < 9999 else datetime.max
        else:
            fim = datetime(ano, mes + 1, 1)
        return mes, ano, inicio, fim

    def movimentacoes_do_periodo(tipo, inicio, fim):
        return (
            Movimentacao.query
            .filter(
                Movimentacao.tipo == tipo,
                Movimentacao.data >= inicio,
                Movimentacao.data < fim,
            )
            .order_by(Movimentacao.data)
            .all()
        )

    @blueprint.get("/financeiro")
    def pagina_financeiro():
        return render_template("financeiro.html")

    @blueprint.get("/relatorios")
    def pagina_relatorios():
        return render_template("relatorios.html")

    @blueprint.get("/api/financeiro/taxas")
    def listar_taxas():
        taxas = ConfiguracaoTaxa.query.order_by(ConfiguracaoTaxa.forma_pagamento).all()
        return jsonify([serializar_taxa(taxa) for taxa in taxas])

    @blueprint.put("/api/financeiro/taxas")
    def atualizar_taxas():
        try:
            payload = ler_payload()
            itens = payload.get("taxas")
            if not isinstance(itens, list):
                raise ValueError("'taxas' deve ser uma lista.")

            atualizacoes = []
            for item in itens:
                if not isinstance(item, dict):
                    raise ValueError("Cada taxa deve ser um objeto.")
                try:
                    forma = FormaPagamento(item.get("forma_pagamento"))
                except (TypeError, ValueError):
                    raise ValueError("Forma de pagamento inválida.") from None
                atualizacoes.append((forma, ler_percentual(item.get("percentual"))))

            for forma, percentual in atualizacoes:
                configuracao = db.session.get(ConfiguracaoTaxa, forma)
                if configuracao is None:
                    configuracao = ConfiguracaoTaxa(forma_pagamento=forma)
                configuracao.percentual = percentual
                db.session.add(configuracao)
            db.session.commit()
        except ValueError as exc:
            db.session.rollback()
            return api_error(str(exc))

        taxas = ConfiguracaoTaxa.query.order_by(ConfiguracaoTaxa.forma_pagamento).all()
        return jsonify([serializar_taxa(taxa) for taxa in taxas])

    @blueprint.post("/api/financeiro/movimentacao")
    def registrar_movimentacao():
        try:
            payload = ler_payload()
            tipo = TipoMovimentacao(payload.get("tipo"))
            forma = FormaPagamento(payload.get("forma_pagamento"))
            descricao = payload.get("descricao")
            categoria = payload.get("categoria")
            profissional = payload.get("profissional") or "Salão"
            valor = float(payload.get("valor"))
            if not isinstance(descricao, str) or not descricao.strip():
                raise ValueError("'descricao' é obrigatória.")
            if not isinstance(categoria, str) or not categoria.strip():
                raise ValueError("'categoria' é obrigatória.")
            if not isinstance(profissional, str):
                raise ValueError("'profissional' deve ser um texto.")
            if not math.isfinite(valor) or valor <= 0:
                raise ValueError("'valor' deve ser um número maior que zero.")
        except (TypeError, ValueError) as exc:
            return api_error(str(exc) or "Tipo ou forma de pagamento inválida.")

        taxa_cartao = 0.0
        valor_liquido = valor
        if tipo == TipoMovimentacao.ENTRADA:
            taxa_cartao = round(valor * obter_taxa_percentual(forma) / 100, 2)
            valor_liquido = round(valor - taxa_cartao, 2)

        movimentacao = Movimentacao(
            tipo=tipo,
            profissional=profissional.strip(),
            descricao=descricao.strip(),
            categoria=categoria.strip(),
            forma_pagamento=forma,
            valor_bruto=valor,
            taxa_cartao=taxa_cartao,
            valor_liquido=valor_liquido,
        )
        db.session.add(movimentacao)
        db.session.commit()
        db.session.refresh(movimentacao)
        return jsonify(serializar_movimentacao(movimentacao))

    @blueprint.get("/api/financeiro/movimentacoes")
    def listar_movimentacoes():
        movimentacoes = Movimentacao.query.order_by(Movimentacao.data.desc()).all()
        return jsonify([serializar_movimentacao(item) for item in movimentacoes])

    @blueprint.post("/api/financeiro/fechamento")
    def fechar_caixa():
        try:
            data_ref = request.args.get("data_ref")
            alvo = date.fromisoformat(data_ref) if data_ref else date.today()
        except ValueError:
            return api_error("'data_ref' deve estar no formato AAAA-MM-DD.")

        inicio = datetime.combine(alvo, time.min)
        fim = datetime.combine(alvo + timedelta(days=1), time.min)
        movimentacoes = Movimentacao.query.filter(
            Movimentacao.data >= inicio,
            Movimentacao.data < fim,
        ).all()
        entradas = sum(item.valor_bruto for item in movimentacoes if item.tipo == TipoMovimentacao.ENTRADA)
        saidas = sum(item.valor_bruto for item in movimentacoes if item.tipo == TipoMovimentacao.SAIDA)
        taxas = sum(item.taxa_cartao or 0.0 for item in movimentacoes if item.tipo == TipoMovimentacao.ENTRADA)
        saldo = round(entradas - saidas - taxas, 2)

        fechamento = FechamentoCaixa.query.filter_by(data_fechamento=alvo).first()
        if fechamento is None:
            fechamento = FechamentoCaixa(data_fechamento=alvo)
        fechamento.total_entradas = entradas
        fechamento.total_saidas = saidas
        fechamento.total_taxas = taxas
        fechamento.saldo_liquido = saldo
        db.session.add(fechamento)
        db.session.commit()

        return jsonify(
            data=alvo.isoformat(),
            total_entradas=entradas,
            total_saidas=saidas,
            total_taxas=taxas,
            saldo_liquido=saldo,
        )

    @blueprint.get("/api/relatorios/consolidado")
    def obter_relatorio_consolidado():
        try:
            mes, ano, inicio, fim = ler_periodo_relatorio()
        except ValueError as exc:
            return api_error(str(exc))

        entradas = movimentacoes_do_periodo(TipoMovimentacao.ENTRADA, inicio, fim)
        saidas = movimentacoes_do_periodo(TipoMovimentacao.SAIDA, inicio, fim)
        faturamento = sum(item.valor_bruto for item in entradas)
        despesas = sum(item.valor_bruto for item in saidas)
        taxas = sum(item.taxa_cartao or 0.0 for item in entradas)
        total_atendimentos = len(entradas)
        semanas = [0.0, 0.0, 0.0, 0.0]
        for item in entradas:
            semanas[min((item.data.day - 1) // 7, 3)] += item.valor_bruto
        servicos = [
            {"nome": nome, "quantidade": quantidade, "percentual": f"{round(quantidade / total_atendimentos * 100, 1)}%"}
            for nome, quantidade in Counter(item.categoria for item in entradas).most_common(4)
        ] if total_atendimentos else []

        return jsonify(
            faturamento_mensal=faturamento,
            total_despesas=despesas,
            saldo_liquido=round(faturamento - despesas - taxas, 2),
            ticket_medio=round(faturamento / total_atendimentos, 2) if total_atendimentos else 0.0,
            taxa_ocupacao=f"{min(round(total_atendimentos / 176 * 100, 1), 100.0)}%",
            total_atendimentos=total_atendimentos,
            servicos_mais_realizados=servicos,
            faturamento_semanal=semanas,
        )

    @blueprint.get("/api/relatorios/exportar-pdf")
    def exportar_relatorio_pdf():
        try:
            mes, ano, inicio, fim = ler_periodo_relatorio()
        except ValueError as exc:
            return api_error(str(exc))

        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

        entradas = movimentacoes_do_periodo(TipoMovimentacao.ENTRADA, inicio, fim)
        saidas = movimentacoes_do_periodo(TipoMovimentacao.SAIDA, inicio, fim)
        faturamento = sum(item.valor_bruto for item in entradas)
        despesas = sum(item.valor_bruto for item in saidas)
        taxas = sum(item.taxa_cartao or 0.0 for item in entradas)
        saldo = round(faturamento - despesas - taxas, 2)
        formatar_moeda = lambda valor: f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        buffer = io.BytesIO()
        documento = SimpleDocTemplate(buffer, pagesize=letter)
        estilos = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle(
            "TituloSRBeauty",
            parent=estilos["Heading1"],
            fontSize=18,
            textColor=colors.HexColor("#8C4A5A"),
        )
        estilo_celula = ParagraphStyle(
            "CelulaSRBeauty",
            parent=estilos["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#343434"),
        )
        elementos = [
            Paragraph("SR Beauty — Relatório Gerencial Financeiro", estilo_titulo),
            Paragraph(f"Referência: {mes:02d}/{ano}", estilos["Normal"]),
            Spacer(1, 15),
        ]
        resumo = [
            ["Indicador", "Valor"],
            ["Faturamento mensal", formatar_moeda(faturamento)],
            ["Despesas do mês", formatar_moeda(despesas)],
            ["Taxas de cartão", formatar_moeda(taxas)],
            ["Saldo líquido", formatar_moeda(saldo)],
            ["Atendimentos realizados", str(len(entradas))],
        ]
        tabela_resumo = Table(resumo, colWidths=[250, 200])
        tabela_resumo.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#8C4A5A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E2DE")),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        elementos.extend([tabela_resumo, Spacer(1, 15)])

        for titulo, movimentacoes, cor, valor_fn in (
            ("Recebimentos (Entradas)", entradas, "#8FA89A", lambda item: item.valor_liquido),
            ("Despesas (Saídas)", saidas, "#A44848", lambda item: item.valor_bruto),
        ):
            elementos.append(Paragraph(f"<b>{titulo}</b>", estilos["Heading2"]))
            linhas = [["Data", "Profissional", "Descrição", "Categoria", "Forma", "Valor"]]
            for item in movimentacoes:
                linhas.append([
                    item.data.strftime("%d/%m/%Y"),
                    escape(item.profissional or "Salão"),
                    Paragraph(escape(item.descricao), estilo_celula),
                    escape(item.categoria),
                    item.forma_pagamento.value.upper(),
                    formatar_moeda(valor_fn(item)),
                ])
            if not movimentacoes:
                linhas.append(["-", "-", "Nenhuma movimentação no período", "-", "-", "R$ 0,00"])
            tabela = Table(linhas, colWidths=[65, 85, 130, 85, 75, 80])
            tabela.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(cor)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E2DE")),
                ("PADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            elementos.extend([tabela, Spacer(1, 15)])

        documento.build(elementos)
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"Relatorio_SRBeauty_{mes:02d}_{ano}.pdf",
        )

    return blueprint, Movimentacao, FechamentoCaixa, ConfiguracaoTaxa


def inicializar_taxas_padrao(db, ConfiguracaoTaxa, FormaPagamento):
    if ConfiguracaoTaxa.query.count() == 0:
        db.session.add_all([
            ConfiguracaoTaxa(forma_pagamento=FormaPagamento.PIX, percentual=0.0),
            ConfiguracaoTaxa(forma_pagamento=FormaPagamento.DINHEIRO, percentual=0.0),
            ConfiguracaoTaxa(forma_pagamento=FormaPagamento.CARTAO_DEBITO, percentual=1.99),
            ConfiguracaoTaxa(forma_pagamento=FormaPagamento.CARTAO_CREDITO, percentual=3.99),
        ])
        db.session.commit()


def migrar_banco_financeiro_legado(
    db,
    Movimentacao,
    FechamentoCaixa,
    ConfiguracaoTaxa,
    caminho_origem,
):
    caminho_origem = Path(caminho_origem)
    if not caminho_origem.is_file():
        raise FileNotFoundError(f"Banco financeiro legado não encontrado: {caminho_origem}")

    origem = sqlite3.connect(
        f"file:{caminho_origem.resolve().as_posix()}?mode=ro",
        uri=True,
    )
    origem.row_factory = sqlite3.Row
    try:
        tabelas = {
            row["name"]
            for row in origem.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        esperadas = {"movimentacoes", "fechamentos_caixa", "configuracao_taxas"}
        if not esperadas.issubset(tabelas):
            raise ValueError("O banco financeiro legado não contém todas as tabelas esperadas.")

        movimentacoes = origem.execute("SELECT * FROM movimentacoes ORDER BY id").fetchall()
        fechamentos = origem.execute("SELECT * FROM fechamentos_caixa ORDER BY id").fetchall()
        configuracoes = origem.execute("SELECT * FROM configuracao_taxas").fetchall()
    finally:
        origem.close()

    def converter_enum(tipo_enum, valor):
        try:
            return tipo_enum[valor]
        except KeyError:
            return tipo_enum(valor.lower())

    def converter_datetime(valor):
        return datetime.fromisoformat(valor) if valor else None

    def mesmos_valores(registro, valores):
        for campo, valor in valores.items():
            atual = getattr(registro, campo)
            if isinstance(valor, float):
                if atual is None or not math.isclose(atual, valor, rel_tol=1e-9, abs_tol=1e-9):
                    return False
            elif atual != valor:
                return False
        return True

    importados = {"movimentacoes": 0, "fechamentos": 0, "taxas": 0}
    try:
        for linha in movimentacoes:
            valores = {
                "tipo": converter_enum(TipoMovimentacao, linha["tipo"]),
                "profissional": linha["profissional"],
                "descricao": linha["descricao"],
                "categoria": linha["categoria"],
                "forma_pagamento": converter_enum(FormaPagamento, linha["forma_pagamento"]),
                "valor_bruto": linha["valor_bruto"],
                "taxa_cartao": linha["taxa_cartao"],
                "valor_liquido": linha["valor_liquido"],
                "data": converter_datetime(linha["data"]),
            }
            existente = db.session.get(Movimentacao, linha["id"])
            if existente:
                if not mesmos_valores(existente, valores):
                    raise ValueError(f"Conflito no ID {linha['id']} da tabela movimentacoes.")
                continue
            db.session.add(Movimentacao(id=linha["id"], **valores))
            importados["movimentacoes"] += 1

        for linha in fechamentos:
            valores = {
                "data_fechamento": date.fromisoformat(linha["data_fechamento"]),
                "total_entradas": linha["total_entradas"],
                "total_saidas": linha["total_saidas"],
                "total_taxas": linha["total_taxas"],
                "saldo_liquido": linha["saldo_liquido"],
                "data_hora_registro": converter_datetime(linha["data_hora_registro"]),
            }
            existente = db.session.get(FechamentoCaixa, linha["id"])
            if existente is None:
                existente = FechamentoCaixa.query.filter_by(
                    data_fechamento=valores["data_fechamento"]
                ).first()
            if existente:
                if not mesmos_valores(existente, valores):
                    raise ValueError(
                        f"Conflito no fechamento de {valores['data_fechamento'].isoformat()}."
                    )
                continue
            db.session.add(FechamentoCaixa(id=linha["id"], **valores))
            importados["fechamentos"] += 1

        taxas_padrao = {
            FormaPagamento.PIX: 0.0,
            FormaPagamento.DINHEIRO: 0.0,
            FormaPagamento.CARTAO_DEBITO: 1.99,
            FormaPagamento.CARTAO_CREDITO: 3.99,
        }
        for linha in configuracoes:
            forma = converter_enum(FormaPagamento, linha["forma_pagamento"])
            percentual = float(linha["percentual"])
            existente = db.session.get(ConfiguracaoTaxa, forma)
            if existente:
                if math.isclose(existente.percentual, percentual, rel_tol=1e-9, abs_tol=1e-9):
                    continue
                if not math.isclose(
                    existente.percentual,
                    taxas_padrao[forma],
                    rel_tol=1e-9,
                    abs_tol=1e-9,
                ):
                    raise ValueError(
                        f"Conflito na taxa de {forma.value}; revise antes da migração."
                    )
                existente.percentual = percentual
            else:
                db.session.add(ConfiguracaoTaxa(forma_pagamento=forma, percentual=percentual))
            importados["taxas"] += 1

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return importados
