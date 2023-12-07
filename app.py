from flask import Flask, request, render_template,url_for,redirect,flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import login_required,LoginManager,UserMixin,logout_user, login_user
from datetime import timedelta, datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
load_dotenv(override=True)
#CONFIGURAÇÕES DE BANCO DE DADOS
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]= os.environ["SQLITE"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#CONFIGURAÇÕES DE LOGIN
login_manager=LoginManager(app)
login_manager.login_view = "index"
login_manager.login_message_category = "Realize o login para acessar esta página"

@login_manager.user_loader
def current_user(user_id):
    return usuario.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    flash("Realize o login para acessar esta página")
    return redirect(url_for('login'))

#BANCO DE DADOS - CADASTRO DE USUARIO
class usuario(db.Model, UserMixin):
    __tablename__="usuario"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True, index=True)
    senha = db.Column(db.String(255), nullable=False)
    ultimologin = db.Column(db.Date)
    
    def __init__(self, nome, email, senha):
        self.nome = nome
        self.email = email
        self.senha = senha

#ROTA PARA LOGIN    
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]    
        userlog = usuario.query.filter_by(email=email).first()
        if not userlog:
            flash("Usuario Incorreto")
            return redirect(url_for('login'))
        if not check_password_hash(userlog.senha, senha):
            flash("Senha Incorreta")
            return redirect(url_for('login'))
        else:
            login_user(userlog, duration=timedelta(hours=1))
            session["username"] = userlog.nome
            session['logged_in']=True
            print("Usuário logado: " + str(userlog.nome))
            setattr(userlog, "ultimologin", datetime.now())
            db.session.commit()
            return redirect(url_for('home'))
    return render_template("index.html")

#ROTA PARA CADASTRO
@app.route("/cadastro", methods=["POST", "GET"])
def cadastro():
    if request.method == "POST":
        nome =  request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"] 
        
        if not nome or not email or not senha:
            flash("Por favor preencha todos os campos") 
            return redirect(url_for('cadastro'))
        else:
            salvar = usuario(nome, email, generate_password_hash(senha))
            setattr(salvar, "ultimologin", datetime.now())
            db.session.add(salvar)
            db.session.commit()
            flash(f"cadastro de {nome}")
            return redirect(url_for('login'))
    return render_template("cadastro.html")

@app.route("/")
def redi():
    if 'logged_in' in session:
        return redirect("/home")
    else:
        return render_template("index.html")
    

#ROTA HOME
@app.route('/home', methods=["POST", "GET"])
@login_required
def home():
    if 'username' in session:
        name= session['username']
    return render_template("home.html", name=name)

#ROTA PARA SAIR
@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop("logged_in")
    return redirect(url_for('login'))

#ROTA PARA TROCAR DE SENHA
@app.route("/trocasenha", methods=["GET", "POST"])
def trocasenha():
    if request.method == "POST":
        email2 = request.form["email"]
        senha_nova = request.form["senha"]
        try:
            troca = usuario.query.filter_by(email = email2).first()
            setattr(troca, 'senha', generate_password_hash(senha_nova))
            db.session.commit()
            flash('feito')
        except:
            flash('seu email esta incorreto')
            return redirect(url_for('trocasenha'))
        return redirect(url_for('login'))
    return render_template("troca_senha.html")


if __name__ == "__main__":
    app.run(debug=True, port=9000)