import os
from datetime import datetime, timezone
from datetime import date as date_type, time as time_type, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import Flask, abort, flash, jsonify, redirect, render_template, request, send_from_directory, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-change-me")

database_url = os.getenv("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or f"sqlite:///{BASE_DIR / 'srbeauty.db'}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
SALON_TIMEZONE = ZoneInfo("America/Sao_Paulo")
WEEKDAY_NAMES = ("Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo")
login_manager.login_view = "login"
login_manager.login_message = "Faça login para acessar esta página."
login_manager.login_message_category = "info"


class User(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(30), nullable=False, default="cliente")

    def set_password(self, password: str) -> None:
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.senha_hash, password)

    @property
    def tipo_label(self) -> str:
        return {
            "cliente": "Cliente",
            "profissional": "Profissional",
            "proprietario": "Proprietário",
        }.get(self.tipo, self.tipo.title())


class Service(db.Model):
    __tablename__ = "servicos"
    __table_args__ = (
        db.CheckConstraint("preco >= 0", name="ck_servicos_preco_nao_negativo"),
        db.CheckConstraint("duracao_minutos > 0", name="ck_servicos_duracao_positiva"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.String(1000), nullable=False, default="")
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    duracao_minutos = db.Column(db.Integer, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    criado_em = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    atualizado_em = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Appointment(db.Model):
    __tablename__ = "atendimentos"
    __table_args__ = (
        db.CheckConstraint(
            "status IN ('aguardando', 'em_atendimento', 'concluido')",
            name="ck_atendimentos_status",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    profissional_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    agendamento_id = db.Column(db.Integer, nullable=True, index=True)
    agendado_para = db.Column(db.DateTime(timezone=True), nullable=False)
    iniciado_em = db.Column(db.DateTime(timezone=True), nullable=True)
    concluido_em = db.Column(db.DateTime(timezone=True), nullable=True)
    duracao_real_minutos = db.Column(db.Integer, nullable=True)
    observacoes = db.Column(db.String(1000), nullable=False, default="")
    status = db.Column(db.String(20), nullable=False, default="aguardando")
    criado_em = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    itens = db.relationship(
        "AppointmentService",
        back_populates="atendimento",
        cascade="all, delete-orphan",
        order_by="AppointmentService.id",
    )


class AppointmentService(db.Model):
    __tablename__ = "atendimento_servicos"
    __table_args__ = (
        db.CheckConstraint("valor_cobrado >= 0", name="ck_atendimento_servicos_valor_nao_negativo"),
        db.CheckConstraint("duracao_prevista_minutos > 0", name="ck_atendimento_servicos_duracao_positiva"),
    )

    id = db.Column(db.Integer, primary_key=True)
    atendimento_id = db.Column(db.Integer, db.ForeignKey("atendimentos.id", ondelete="CASCADE"), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey("servicos.id", ondelete="RESTRICT"), nullable=False)
    profissional_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    nome_servico = db.Column(db.String(120), nullable=False)
    valor_cobrado = db.Column(db.Numeric(10, 2), nullable=False)
    duracao_prevista_minutos = db.Column(db.Integer, nullable=False)
    atendimento = db.relationship("Appointment", back_populates="itens")


class ProfessionalSchedule(db.Model):
    __tablename__ = "horarios_profissionais"
    __table_args__ = (
        db.CheckConstraint("dia_semana BETWEEN 0 AND 6", name="ck_horarios_dia_semana"),
    )

    id = db.Column(db.Integer, primary_key=True)
    profissional_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    dia_semana = db.Column(db.Integer, nullable=False)
    inicio = db.Column(db.Time, nullable=False)
    fim = db.Column(db.Time, nullable=False)


class AgendaBlock(db.Model):
    __tablename__ = "bloqueios_agenda"
    __table_args__ = (
        db.CheckConstraint("fim > inicio", name="ck_bloqueios_periodo_valido"),
    )

    id = db.Column(db.Integer, primary_key=True)
    profissional_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    inicio = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    fim = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    motivo = db.Column(db.String(120), nullable=False)


class AgendaConflictError(Exception):
    pass


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def api_error(message, status_code):
    return jsonify({"erro": message}), status_code


def positive_integer(value, field):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"'{field}' deve ser um número inteiro positivo.")
    return value


def parse_money(value, field):
    if isinstance(value, bool) or value is None:
        raise ValueError(f"'{field}' deve ser um número maior ou igual a zero.")
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"'{field}' deve ser um número maior ou igual a zero.") from None
    if not amount.is_finite() or amount < 0 or amount.as_tuple().exponent < -2:
        raise ValueError(f"'{field}' deve ser um número não negativo com até duas casas decimais.")
    if amount >= Decimal("100000000"):
        raise ValueError(f"'{field}' excede o valor máximo permitido.")
    return amount.quantize(Decimal("0.01"))


def parse_datetime(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"'{field}' deve ser uma data e hora ISO 8601.")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        raise ValueError(f"'{field}' deve ser uma data e hora ISO 8601 válida.") from None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"'{field}' deve incluir o fuso horário (por exemplo, -03:00 ou Z).")
    return parsed.astimezone(timezone.utc)


def as_utc(value):
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def datetime_json(value):
    return as_utc(value).isoformat() if value else None


def parse_notes(value):
    if not isinstance(value, str) or len(value) > 1000:
        raise ValueError("'observacoes' deve ser um texto de até 1000 caracteres.")
    return value.strip()


def valid_user(user_id, role, field):
    user = db.session.get(User, user_id)
    if user is None or user.tipo != role:
        raise ValueError(f"'{field}' deve identificar um usuário existente do tipo {role}.")
    return user


def agenda_access_error():
    if not current_user.is_authenticated:
        return api_error("Autenticação necessária.", 401)
    if current_user.tipo not in {"profissional", "proprietario"}:
        return api_error("A agenda está disponível apenas para profissionais e proprietárias.", 403)
    return None


def authorized_professional_ids(requested_id=None):
    if current_user.tipo == "profissional":
        if requested_id is not None and requested_id != current_user.id:
            return None, api_error("Você só pode acessar a própria agenda.", 403)
        return [current_user.id], None
    query = User.query.filter_by(tipo="profissional")
    if requested_id is not None:
        professional = query.filter_by(id=requested_id).first()
        if professional is None:
            return None, api_error("Profissional não encontrado.", 404)
        return [professional.id], None
    return [user.id for user in query.order_by(User.nome).all()], None


def parse_schedule_time(value, field):
    if not isinstance(value, str) or len(value) != 5 or value[2] != ":":
        raise ValueError(f"'{field}' deve usar o formato HH:MM.")
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError:
        raise ValueError(f"'{field}' deve ser um horário válido no formato HH:MM.") from None


def parse_weekday(value):
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 6:
        raise ValueError("'dia_semana' deve ser um inteiro de 0 (segunda-feira) a 6 (domingo).")
    return value


def schedule_json(schedule):
    return {
        "id": schedule.id,
        "profissional_id": schedule.profissional_id,
        "dia_semana": schedule.dia_semana,
        "dia_semana_nome": WEEKDAY_NAMES[schedule.dia_semana],
        "inicio": schedule.inicio.strftime("%H:%M"),
        "fim": schedule.fim.strftime("%H:%M"),
    }


def block_json(block):
    return {
        "id": block.id,
        "profissional_id": block.profissional_id,
        "inicio": datetime_json(block.inicio),
        "fim": datetime_json(block.fim),
        "motivo": block.motivo,
    }


def validate_schedule_interval(professional_id, weekday, starts, ends, excluding_id=None):
    if starts >= ends:
        raise ValueError("'fim' deve ser posterior a 'inicio'.")
    query = ProfessionalSchedule.query.filter_by(
        profissional_id=professional_id,
        dia_semana=weekday,
    )
    if excluding_id is not None:
        query = query.filter(ProfessionalSchedule.id != excluding_id)
    if any(starts < item.fim and ends > item.inicio for item in query.all()):
        raise AgendaConflictError("Esse horário se sobrepõe a outro período de funcionamento.")


def appointment_duration_for_professional(appointment, professional_id):
    matching = [
        item.duracao_prevista_minutos
        for item in appointment.itens
        if item.profissional_id == professional_id
    ]
    if matching:
        return sum(matching)
    if not appointment.itens and appointment.profissional_id == professional_id:
        return 1
    return 0


def ensure_professional_available(
    professional_id,
    starts,
    ends,
    excluding_appointment_id=None,
    excluding_block_id=None,
):
    local_start = starts.astimezone(SALON_TIMEZONE)
    local_end = ends.astimezone(SALON_TIMEZONE)
    weekly_schedules = ProfessionalSchedule.query.filter_by(profissional_id=professional_id).all()
    if weekly_schedules:
        matching_day = [
            item for item in weekly_schedules if item.dia_semana == local_start.weekday()
        ]
        if not any(
            item.inicio <= local_start.time().replace(tzinfo=None)
            and local_end.date() == local_start.date()
            and local_end.time().replace(tzinfo=None) <= item.fim
            for item in matching_day
        ):
            raise AgendaConflictError("O horário solicitado está fora da escala de funcionamento da profissional.")

    blocked_query = AgendaBlock.query.filter(
        AgendaBlock.profissional_id == professional_id,
        AgendaBlock.inicio < ends,
        AgendaBlock.fim > starts,
    )
    if excluding_block_id is not None:
        blocked_query = blocked_query.filter(AgendaBlock.id != excluding_block_id)
    blocked = blocked_query.first()
    if blocked:
        raise AgendaConflictError(f"Conflito com o bloqueio de agenda: {blocked.motivo}.")

    appointments = (
        Appointment.query.options(selectinload(Appointment.itens))
        .filter(Appointment.status != "concluido", Appointment.agendado_para < ends)
        .all()
    )
    for appointment in appointments:
        if appointment.id == excluding_appointment_id:
            continue
        duration = appointment_duration_for_professional(appointment, professional_id)
        if duration <= 0:
            continue
        existing_start = as_utc(appointment.agendado_para)
        existing_end = existing_start + timedelta(minutes=duration)
        if existing_start < ends and existing_end > starts:
            raise AgendaConflictError("A profissional já possui um atendimento nesse intervalo.")


def appointment_service_durations(appointment):
    durations = {}
    for item in appointment.itens:
        durations[item.profissional_id] = (
            durations.get(item.profissional_id, 0) + item.duracao_prevista_minutos
        )
    if not durations and appointment.profissional_id:
        durations[appointment.profissional_id] = 1
    return durations


def lock_appointment_professionals(professional_ids):
    statement = db.select(User).where(User.id.in_(sorted(professional_ids))).order_by(User.id)
    if db.engine.dialect.name == "sqlite":
        # SQLite ignores FOR UPDATE, so acquire its writer lock before checking availability.
        db.session.execute(
            db.update(User)
            .where(User.id.in_(sorted(professional_ids)))
            .values(id=User.id)
        )
        return
    db.session.execute(statement.with_for_update()).scalars().all()


def parse_agenda_date(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Informe '{field}' no formato AAAA-MM-DD.")
    try:
        return date_type.fromisoformat(value)
    except ValueError:
        raise ValueError(f"'{field}' deve ser uma data válida no formato AAAA-MM-DD.") from None


def agenda_range_events(start_date, end_date, professional_ids):
    local_start = datetime.combine(start_date, time_type.min, SALON_TIMEZONE)
    local_end = datetime.combine(end_date + timedelta(days=1), time_type.min, SALON_TIMEZONE)
    utc_start = local_start.astimezone(timezone.utc)
    utc_end = local_end.astimezone(timezone.utc)
    schedules = ProfessionalSchedule.query.filter(
        ProfessionalSchedule.profissional_id.in_(professional_ids),
        ProfessionalSchedule.dia_semana.in_(
            [(start_date + timedelta(days=offset)).weekday()
             for offset in range((end_date - start_date).days + 1)]
        ),
    ).order_by(ProfessionalSchedule.dia_semana, ProfessionalSchedule.inicio).all() if professional_ids else []
    blocks = AgendaBlock.query.filter(
        AgendaBlock.profissional_id.in_(professional_ids),
        AgendaBlock.inicio < utc_end,
        AgendaBlock.fim > utc_start,
    ).order_by(AgendaBlock.inicio).all() if professional_ids else []
    appointments = (
        Appointment.query.options(selectinload(Appointment.itens))
        .filter(
            Appointment.agendado_para < utc_end,
        )
        .order_by(Appointment.agendado_para)
        .all()
    )
    directory = {
        user.id: user.nome
        for user in User.query.filter(
            User.id.in_(
                professional_ids
                + [appointment.cliente_id for appointment in appointments]
                + [appointment.profissional_id for appointment in appointments]
            )
        ).all()
    } if professional_ids else {}

    events = []
    for block in blocks:
        events.append({
            "tipo": "bloqueio",
            **block_json(block),
            "profissional_nome": directory.get(block.profissional_id, ""),
        })
    for appointment in appointments:
        start = as_utc(appointment.agendado_para)
        for professional_id, duration in appointment_service_durations(appointment).items():
            if professional_id not in professional_ids:
                continue
            end = start + timedelta(minutes=duration)
            if start >= utc_end or end <= utc_start:
                continue
            events.append({
                "tipo": "atendimento",
                "id": appointment.id,
                "inicio": datetime_json(start),
                "fim": datetime_json(end),
                "cliente_id": appointment.cliente_id,
                "cliente_nome": directory.get(appointment.cliente_id, ""),
                "profissional_id": professional_id,
                "profissional_nome": directory.get(professional_id, ""),
                "servicos": [
                    item.nome_servico
                    for item in appointment.itens
                    if item.profissional_id == professional_id
                ],
                "status": appointment.status,
                "observacoes": appointment.observacoes,
            })
    events.sort(key=lambda item: item["inicio"])
    return {
        "inicio": start_date.isoformat(),
        "fim": end_date.isoformat(),
        "eventos": events,
        "horarios": [schedule_json(item) for item in schedules],
        "profissionais": [
            {"id": user.id, "nome": user.nome}
            for user in User.query.filter(User.id.in_(professional_ids)).order_by(User.nome).all()
        ] if professional_ids else [],
    }


def service_json(service):
    return {
        "id": service.id,
        "nome": service.nome,
        "descricao": service.descricao,
        "preco": format(service.preco, ".2f"),
        "duracao_minutos": service.duracao_minutos,
        "ativo": service.ativo,
        "criado_em": datetime_json(service.criado_em),
        "atualizado_em": datetime_json(service.atualizado_em),
    }


def appointment_json(appointment):
    return {
        "id": appointment.id,
        "cliente_id": appointment.cliente_id,
        "profissional_id": appointment.profissional_id,
        "agendamento_id": appointment.agendamento_id,
        "agendado_para": datetime_json(appointment.agendado_para),
        "iniciado_em": datetime_json(appointment.iniciado_em),
        "concluido_em": datetime_json(appointment.concluido_em),
        "duracao_real_minutos": appointment.duracao_real_minutos,
        "observacoes": appointment.observacoes,
        "status": appointment.status,
        "servicos": [
            {
                "id": item.id,
                "servico_id": item.servico_id,
                "nome_servico": item.nome_servico,
                "profissional_id": item.profissional_id,
                "valor_cobrado": format(item.valor_cobrado, ".2f"),
                "duracao_prevista_minutos": item.duracao_prevista_minutos,
            }
            for item in appointment.itens
        ],
    }


def can_manage_professional(professional_id):
    return current_user.tipo == "proprietario" or (
        current_user.tipo == "profissional" and current_user.id == professional_id
    )


@app.route("/api/horarios", methods=["GET", "POST"])
def api_horarios():
    access_error = agenda_access_error()
    if access_error:
        return access_error

    if request.method == "GET":
        requested = request.args.get("profissional_id")
        try:
            requested_id = positive_integer(int(requested), "profissional_id") if requested else None
        except (TypeError, ValueError):
            return api_error("'profissional_id' deve ser um inteiro positivo.", 400)
        professional_ids, error = authorized_professional_ids(requested_id)
        if error:
            return error
        query = ProfessionalSchedule.query
        if professional_ids:
            query = query.filter(ProfessionalSchedule.profissional_id.in_(professional_ids))
        else:
            return jsonify([])
        schedules = query.order_by(
            ProfessionalSchedule.profissional_id,
            ProfessionalSchedule.dia_semana,
            ProfessionalSchedule.inicio,
        ).all()
        return jsonify([schedule_json(schedule) for schedule in schedules])

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error("Envie um objeto JSON válido.", 400)
    try:
        professional_id = positive_integer(data.get("profissional_id"), "profissional_id")
        valid_user(professional_id, "profissional", "profissional_id")
        if not can_manage_professional(professional_id):
            return api_error("Você não pode alterar a escala de outra profissional.", 403)
        weekday = parse_weekday(data.get("dia_semana"))
        starts = parse_schedule_time(data.get("inicio"), "inicio")
        ends = parse_schedule_time(data.get("fim"), "fim")
        validate_schedule_interval(professional_id, weekday, starts, ends)
        schedule = ProfessionalSchedule(
            profissional_id=professional_id,
            dia_semana=weekday,
            inicio=starts,
            fim=ends,
        )
        db.session.add(schedule)
        db.session.commit()
        return jsonify(schedule_json(schedule)), 201
    except AgendaConflictError as error:
        db.session.rollback()
        return api_error(str(error), 409)
    except ValueError as error:
        db.session.rollback()
        return api_error(str(error), 400)


@app.route("/api/horarios/lote", methods=["POST"])
def api_horarios_lote():
    access_error = agenda_access_error()
    if access_error:
        return access_error
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error("Envie um objeto JSON válido.", 400)
    try:
        professional_id = positive_integer(data.get("profissional_id"), "profissional_id")
        valid_user(professional_id, "profissional", "profissional_id")
        if not can_manage_professional(professional_id):
            return api_error("Você não pode alterar a escala de outra profissional.", 403)
        raw_weekdays = data.get("dias_semana")
        if not isinstance(raw_weekdays, list) or not raw_weekdays:
            raise ValueError("'dias_semana' deve conter ao menos um dia.")
        weekdays = [parse_weekday(weekday) for weekday in raw_weekdays]
        if len(set(weekdays)) != len(weekdays):
            raise ValueError("'dias_semana' não pode conter dias repetidos.")
        starts = parse_schedule_time(data.get("inicio"), "inicio")
        ends = parse_schedule_time(data.get("fim"), "fim")

        for weekday in weekdays:
            validate_schedule_interval(professional_id, weekday, starts, ends)

        schedules = [
            ProfessionalSchedule(
                profissional_id=professional_id,
                dia_semana=weekday,
                inicio=starts,
                fim=ends,
            )
            for weekday in weekdays
        ]
        db.session.add_all(schedules)
        db.session.commit()
        return jsonify([schedule_json(schedule) for schedule in schedules]), 201
    except AgendaConflictError as error:
        db.session.rollback()
        return api_error(str(error), 409)
    except ValueError as error:
        db.session.rollback()
        return api_error(str(error), 400)


@app.route("/api/horarios/<int:schedule_id>", methods=["GET", "PUT", "DELETE"])
def api_horario_detalhe(schedule_id):
    access_error = agenda_access_error()
    if access_error:
        return access_error
    schedule = db.session.get(ProfessionalSchedule, schedule_id)
    if schedule is None:
        return api_error("Horário não encontrado.", 404)
    if not can_manage_professional(schedule.profissional_id):
        return api_error("Você não pode acessar a escala de outra profissional.", 403)
    if request.method == "GET":
        return jsonify(schedule_json(schedule))
    if request.method == "DELETE":
        db.session.delete(schedule)
        db.session.commit()
        return "", 204

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error("Envie um objeto JSON válido.", 400)
    try:
        weekday = parse_weekday(data.get("dia_semana"))
        starts = parse_schedule_time(data.get("inicio"), "inicio")
        ends = parse_schedule_time(data.get("fim"), "fim")
        validate_schedule_interval(
            schedule.profissional_id, weekday, starts, ends, excluding_id=schedule.id
        )
        schedule.dia_semana = weekday
        schedule.inicio = starts
        schedule.fim = ends
        db.session.commit()
        return jsonify(schedule_json(schedule))
    except AgendaConflictError as error:
        db.session.rollback()
        return api_error(str(error), 409)
    except ValueError as error:
        db.session.rollback()
        return api_error(str(error), 400)


@app.route("/api/bloqueios", methods=["GET", "POST"])
def api_bloqueios():
    access_error = agenda_access_error()
    if access_error:
        return access_error

    if request.method == "GET":
        requested = request.args.get("profissional_id")
        try:
            requested_id = positive_integer(int(requested), "profissional_id") if requested else None
        except (TypeError, ValueError):
            return api_error("'profissional_id' deve ser um inteiro positivo.", 400)
        professional_ids, error = authorized_professional_ids(requested_id)
        if error:
            return error
        if not professional_ids:
            return jsonify([])
        blocks = AgendaBlock.query.filter(
            AgendaBlock.profissional_id.in_(professional_ids)
        ).order_by(AgendaBlock.inicio).all()
        return jsonify([block_json(block) for block in blocks])

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error("Envie um objeto JSON válido.", 400)
    try:
        professional_id = positive_integer(data.get("profissional_id"), "profissional_id")
        valid_user(professional_id, "profissional", "profissional_id")
        if not can_manage_professional(professional_id):
            return api_error("Você não pode bloquear a agenda de outra profissional.", 403)
        starts = parse_datetime(data.get("inicio"), "inicio")
        ends = parse_datetime(data.get("fim"), "fim")
        reason = data.get("motivo")
        if starts >= ends:
            raise ValueError("'fim' deve ser posterior a 'inicio'.")
        if not isinstance(reason, str) or not reason.strip() or len(reason.strip()) > 120:
            raise ValueError("'motivo' é obrigatório e deve ter até 120 caracteres.")
        block = AgendaBlock(
            profissional_id=professional_id,
            inicio=starts,
            fim=ends,
            motivo=reason.strip(),
        )
        overlapping = AgendaBlock.query.filter(
            AgendaBlock.profissional_id == professional_id,
            AgendaBlock.inicio < ends,
            AgendaBlock.fim > starts,
        ).first()
        if overlapping:
            raise AgendaConflictError("Esse bloqueio se sobrepõe a outro bloqueio da agenda.")
        ensure_professional_available(professional_id, starts, ends)
        db.session.add(block)
        db.session.commit()
        return jsonify(block_json(block)), 201
    except AgendaConflictError as error:
        db.session.rollback()
        return api_error(str(error), 409)
    except ValueError as error:
        db.session.rollback()
        return api_error(str(error), 400)


@app.route("/api/bloqueios/<int:block_id>", methods=["GET", "PUT", "DELETE"])
def api_bloqueio_detalhe(block_id):
    access_error = agenda_access_error()
    if access_error:
        return access_error
    block = db.session.get(AgendaBlock, block_id)
    if block is None:
        return api_error("Bloqueio não encontrado.", 404)
    if not can_manage_professional(block.profissional_id):
        return api_error("Você não pode acessar o bloqueio de outra profissional.", 403)
    if request.method == "GET":
        return jsonify(block_json(block))
    if request.method == "DELETE":
        db.session.delete(block)
        db.session.commit()
        return "", 204

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error("Envie um objeto JSON válido.", 400)
    try:
        starts = parse_datetime(data.get("inicio"), "inicio")
        ends = parse_datetime(data.get("fim"), "fim")
        reason = data.get("motivo")
        if starts >= ends:
            raise ValueError("'fim' deve ser posterior a 'inicio'.")
        if not isinstance(reason, str) or not reason.strip() or len(reason.strip()) > 120:
            raise ValueError("'motivo' é obrigatório e deve ter até 120 caracteres.")
        overlapping = AgendaBlock.query.filter(
            AgendaBlock.profissional_id == block.profissional_id,
            AgendaBlock.id != block.id,
            AgendaBlock.inicio < ends,
            AgendaBlock.fim > starts,
        ).first()
        if overlapping:
            raise AgendaConflictError("Esse bloqueio se sobrepõe a outro bloqueio da agenda.")
        ensure_professional_available(
            block.profissional_id,
            starts,
            ends,
            excluding_block_id=block.id,
        )
        block.inicio = starts
        block.fim = ends
        block.motivo = reason.strip()
        db.session.commit()
        return jsonify(block_json(block))
    except AgendaConflictError as error:
        db.session.rollback()
        return api_error(str(error), 409)
    except ValueError as error:
        db.session.rollback()
        return api_error(str(error), 400)


@app.route("/api/agenda/diaria", methods=["GET"])
def api_agenda_diaria():
    access_error = agenda_access_error()
    if access_error:
        return access_error
    try:
        requested_date = request.args.get("data")
        selected_date = (
            parse_agenda_date(requested_date, "data")
            if requested_date
            else datetime.now(SALON_TIMEZONE).date()
        )
        requested_professional = request.args.get("profissional_id")
        requested_id = (
            positive_integer(int(requested_professional), "profissional_id")
            if requested_professional
            else None
        )
    except (TypeError, ValueError) as error:
        return api_error(str(error), 400)
    professional_ids, error = authorized_professional_ids(requested_id)
    if error:
        return error
    return jsonify(agenda_range_events(selected_date, selected_date, professional_ids))


@app.route("/api/agenda/semanal", methods=["GET"])
def api_agenda_semanal():
    access_error = agenda_access_error()
    if access_error:
        return access_error
    try:
        requested_week = request.args.get("semana")
        selected_date = (
            parse_agenda_date(requested_week, "semana")
            if requested_week
            else datetime.now(SALON_TIMEZONE).date()
        )
        monday = selected_date - timedelta(days=selected_date.weekday())
        requested_professional = request.args.get("profissional_id")
        requested_id = (
            positive_integer(int(requested_professional), "profissional_id")
            if requested_professional
            else None
        )
    except (TypeError, ValueError) as error:
        return api_error(str(error), 400)
    professional_ids, error = authorized_professional_ids(requested_id)
    if error:
        return error
    return jsonify(agenda_range_events(monday, monday + timedelta(days=6), professional_ids))


@app.route("/api/servicos", methods=["GET", "POST"])
def api_servicos():
    if request.method == "GET":
        include_inactive = request.args.get("incluir_inativos", "false").lower()
        if include_inactive not in {"true", "false"}:
            return api_error("'incluir_inativos' deve ser true ou false.", 400)
        query = Service.query
        if include_inactive != "true":
            query = query.filter_by(ativo=True)
        return jsonify([service_json(service) for service in query.order_by(Service.nome).all()])

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error("Envie um objeto JSON válido.", 400)
    try:
        name = data.get("nome")
        description = data.get("descricao", "")
        duration = positive_integer(data.get("duracao_minutos"), "duracao_minutos")
        price = parse_money(data.get("preco"), "preco")
        if not isinstance(name, str) or not name.strip() or len(name.strip()) > 120:
            raise ValueError("'nome' é obrigatório e deve ter até 120 caracteres.")
        if not isinstance(description, str) or len(description) > 1000:
            raise ValueError("'descricao' deve ser um texto de até 1000 caracteres.")
        service = Service(
            nome=name.strip(),
            descricao=description.strip(),
            preco=price,
            duracao_minutos=duration,
        )
        db.session.add(service)
        db.session.commit()
        return jsonify(service_json(service)), 201
    except ValueError as error:
        db.session.rollback()
        return api_error(str(error), 400)


@app.route("/api/servicos/<int:service_id>", methods=["GET", "PUT", "DELETE"])
def api_servico_detalhe(service_id):
    service = db.session.get(Service, service_id)
    if service is None:
        return api_error("Serviço não encontrado.", 404)
    if request.method == "GET":
        return jsonify(service_json(service))
    if request.method == "DELETE":
        service.ativo = False
        db.session.commit()
        return "", 204

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error("Envie um objeto JSON válido.", 400)
    try:
        name = data.get("nome")
        description = data.get("descricao", "")
        duration = positive_integer(data.get("duracao_minutos"), "duracao_minutos")
        price = parse_money(data.get("preco"), "preco")
        active = data.get("ativo", service.ativo)
        if not isinstance(name, str) or not name.strip() or len(name.strip()) > 120:
            raise ValueError("'nome' é obrigatório e deve ter até 120 caracteres.")
        if not isinstance(description, str) or len(description) > 1000:
            raise ValueError("'descricao' deve ser um texto de até 1000 caracteres.")
        if not isinstance(active, bool):
            raise ValueError("'ativo' deve ser true ou false.")
        service.nome = name.strip()
        service.descricao = description.strip()
        service.preco = price
        service.duracao_minutos = duration
        service.ativo = active
        db.session.commit()
        return jsonify(service_json(service))
    except ValueError as error:
        db.session.rollback()
        return api_error(str(error), 400)


@app.route("/api/atendimentos", methods=["GET", "POST"])
def api_atendimentos():
    if request.method == "GET":
        query = Appointment.query
        status = request.args.get("status")
        if status:
            if status not in {"aguardando", "em_atendimento", "concluido"}:
                return api_error("Status inválido.", 400)
            query = query.filter_by(status=status)
        return jsonify([appointment_json(item) for item in query.order_by(Appointment.agendado_para).all()])

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error("Envie um objeto JSON válido.", 400)
    try:
        client_id = positive_integer(data.get("cliente_id"), "cliente_id")
        professional_id = positive_integer(data.get("profissional_id"), "profissional_id")
        valid_user(client_id, "cliente", "cliente_id")
        valid_user(professional_id, "profissional", "profissional_id")
        scheduled_for = parse_datetime(data.get("agendado_para"), "agendado_para")
        notes = parse_notes(data.get("observacoes", ""))
        external_booking_id = data.get("agendamento_id")
        if external_booking_id is not None:
            external_booking_id = positive_integer(external_booking_id, "agendamento_id")
        service_data = data.get("servicos")
        if not isinstance(service_data, list) or not service_data:
            raise ValueError("'servicos' deve conter pelo menos um serviço.")

        appointment = Appointment(
            cliente_id=client_id,
            profissional_id=professional_id,
            agendamento_id=external_booking_id,
            agendado_para=scheduled_for,
            observacoes=notes,
            status="aguardando",
        )
        seen_services = set()
        for entry in service_data:
            if not isinstance(entry, dict):
                raise ValueError("Cada item de 'servicos' deve ser um objeto JSON.")
            catalog_id = positive_integer(entry.get("servico_id"), "servico_id")
            if catalog_id in seen_services:
                raise ValueError("Não repita o mesmo serviço no atendimento.")
            seen_services.add(catalog_id)
            catalog_service = db.session.get(Service, catalog_id)
            if catalog_service is None or not catalog_service.ativo:
                raise ValueError(f"Serviço {catalog_id} não existe ou está inativo.")
            item_professional_id = positive_integer(
                entry.get("profissional_id", professional_id), "profissional_id"
            )
            valid_user(item_professional_id, "profissional", "profissional_id")
            charged_price = parse_money(
                entry.get("valor_cobrado", catalog_service.preco), "valor_cobrado"
            )
            appointment.itens.append(
                AppointmentService(
                    servico_id=catalog_service.id,
                    profissional_id=item_professional_id,
                    nome_servico=catalog_service.nome,
                    valor_cobrado=charged_price,
                    duracao_prevista_minutos=catalog_service.duracao_minutos,
                )
            )

        professional_durations = appointment_service_durations(appointment)
        if professional_durations:
            lock_appointment_professionals(professional_durations)
        for item_professional_id, duration in professional_durations.items():
            ensure_professional_available(
                item_professional_id,
                scheduled_for,
                scheduled_for + timedelta(minutes=duration),
            )

        db.session.add(appointment)
        db.session.commit()
        return jsonify(appointment_json(appointment)), 201
    except AgendaConflictError as error:
        db.session.rollback()
        return api_error(str(error), 409)
    except ValueError as error:
        db.session.rollback()
        return api_error(str(error), 400)


@app.route("/api/atendimentos/<int:appointment_id>", methods=["GET"])
def api_atendimento_detalhe(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if appointment is None:
        return api_error("Atendimento não encontrado.", 404)
    return jsonify(appointment_json(appointment))


@app.route("/api/atendimentos/<int:appointment_id>/status", methods=["PATCH"])
def api_atendimento_status(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if appointment is None:
        return api_error("Atendimento não encontrado.", 404)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error("Envie um objeto JSON válido.", 400)

    next_status = data.get("status")
    transitions = {"aguardando": "em_atendimento", "em_atendimento": "concluido"}
    if transitions.get(appointment.status) != next_status:
        return api_error("Transição inválida; use aguardando → em_atendimento → concluido.", 409)

    try:
        if next_status == "em_atendimento":
            if set(data) != {"status"}:
                raise ValueError("Informe somente o novo status ao iniciar o atendimento.")
            appointment.status = "em_atendimento"
            appointment.iniciado_em = datetime.now(timezone.utc)
        else:
            unexpected = set(data) - {"status", "duracao_real_minutos", "observacoes", "concluido_em"}
            if unexpected:
                raise ValueError("O pedido contém campos não permitidos.")
            completed_at = parse_datetime(
                data.get("concluido_em", datetime.now(timezone.utc).isoformat()), "concluido_em"
            )
            started_at = as_utc(appointment.iniciado_em)
            if completed_at < started_at:
                raise ValueError("'concluido_em' não pode ser anterior ao início do atendimento.")
            actual_duration = data.get("duracao_real_minutos")
            if actual_duration is None:
                actual_duration = max(
                    1, int((completed_at - started_at).total_seconds() // 60)
                )
            else:
                actual_duration = positive_integer(actual_duration, "duracao_real_minutos")
            appointment.duracao_real_minutos = actual_duration
            appointment.concluido_em = completed_at
            appointment.observacoes = parse_notes(data.get("observacoes", appointment.observacoes))
            appointment.status = "concluido"
        db.session.commit()
        return jsonify(appointment_json(appointment))
    except ValueError as error:
        db.session.rollback()
        return api_error(str(error), 400)


@app.route("/img/<path:filename>")
def documentos_img(filename):
    return send_from_directory(REPO_ROOT / "documentos" / "img", filename)


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        if not email or not senha:
            flash("Preencha e-mail e senha.", "error")
            return render_template("login.html", email=email)

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(senha):
            flash("E-mail ou senha inválidos.", "error")
            return render_template("login.html", email=email)

        login_user(user)
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        confirmar = request.form.get("confirmar_senha", "")
        tipo = request.form.get("tipo", "cliente")
        tipos_validos = {"cliente", "profissional", "proprietario"}

        if not nome or not email or not senha or not confirmar:
            flash("Preencha todos os campos obrigatórios.", "error")
            return render_template("cadastro.html", nome=nome, email=email, tipo=tipo)

        if tipo not in tipos_validos:
            tipo = "cliente"

        if senha != confirmar:
            flash("As senhas não coincidem.", "error")
            return render_template("cadastro.html", nome=nome, email=email, tipo=tipo)

        if len(senha) < 6:
            flash("A senha precisa ter pelo menos 6 caracteres.", "error")
            return render_template("cadastro.html", nome=nome, email=email, tipo=tipo)

        if User.query.filter_by(email=email).first():
            flash("Já existe uma conta com esse e-mail.", "error")
            return render_template("cadastro.html", nome=nome, email=email, tipo=tipo)

        user = User(nome=nome, email=email, tipo=tipo)
        user.set_password(senha)
        db.session.add(user)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Já existe uma conta com esse e-mail.", "error")
            return render_template("cadastro.html", nome=nome, email=email, tipo=tipo)

        login_user(user)
        flash("Conta criada com sucesso!", "success")
        return redirect(url_for("home"))

    return render_template("cadastro.html")


@app.route("/home")
@login_required
def home():
    return render_template("home.html")


@app.route("/servicos")
@login_required
def pagina_servicos():
    return render_template("servicos.html")


@app.route("/atendimentos")
@login_required
def pagina_atendimentos():
    clientes = User.query.filter_by(tipo="cliente").order_by(User.nome).all()
    profissionais = User.query.filter_by(tipo="profissional").order_by(User.nome).all()
    return render_template(
        "atendimentos.html",
        clientes=[{"id": user.id, "nome": user.nome} for user in clientes],
        profissionais=[{"id": user.id, "nome": user.nome} for user in profissionais],
    )


@app.route("/agenda")
@login_required
def pagina_agenda():
    if current_user.tipo not in {"profissional", "proprietario"}:
        abort(403)
    profissionais = User.query.filter_by(tipo="profissional").order_by(User.nome).all()
    return render_template(
        "agenda.html",
        profissionais=[{"id": user.id, "nome": user.nome} for user in profissionais],
    )


@app.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()

        if not nome or not email:
            flash("Nome e e-mail são obrigatórios.", "error")
            return render_template("perfil.html")

        email_owner = User.query.filter(User.email == email, User.id != current_user.id).first()
        if email_owner:
            flash("Esse e-mail já está sendo usado por outra conta.", "error")
            return render_template("perfil.html")

        current_user.nome = nome
        current_user.email = email
        db.session.commit()
        flash("Perfil atualizado com sucesso.", "success")
        return redirect(url_for("perfil"))

    return render_template("perfil.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("login"))


from Repasses.blueprint import create_repasses_blueprint

repasses_blueprint, CategoriaRepasse, RepasseRegistro = create_repasses_blueprint(
    db,
    User,
    Appointment,
    AppointmentService,
)
app.register_blueprint(repasses_blueprint)


@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Banco inicializado.")


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
