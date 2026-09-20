import os
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
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


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


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


@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Banco inicializado.")


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
