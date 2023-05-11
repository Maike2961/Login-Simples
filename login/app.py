from flask import Flask, request, render_template,url_for,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required,LoginManager,UserMixin,logout_user, login_user
from datetime import timedelta, datetime, date

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]= "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SECRET_KEY"] = "aterces25"

db = SQLAlchemy(app)
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


class usuario(db.Model, UserMixin):
    __tablename__="usuario"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True, index=True)
    senha = db.Column(db.String(255), nullable=False)
    
    def __init__(self):
        return self.nome
    
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]    
        userlog = usuario.query.filter_by(email=email).first()
        if not userlog:
            flash("Usuario Incorreto")
            return redirect(url_for('login'))
        userpass = usuario.query.filter_by(senha=senha).first()
        if not userpass:
            flash("Senha Incorreta")
            return redirect(url_for('login'))
        else:
            login_user(userlog, duration=timedelta(hours=1))
            return redirect(url_for('home'))
    return render_template("index.html")

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
            salvar = usuario()
            salvar.nome = nome
            salvar.email = email
            salvar.senha = senha
            db.session.add(salvar)
            db.session.commit()
        return redirect(url_for('login'))
    return render_template("cadastro.html")

@app.route('/home', methods=["POST", "GET"])
@login_required
def home():
    print("1")
    return render_template("home.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/trocasenha", methods=["GET", "POST"])
def trocasenha():
    if request.method == "POST":
        email2 = request.form["email"]
        senha_nova = request.form["senha"]
        try:
            troca = usuario.query.filter_by(email = email2).first()
            setattr(troca, 'senha', senha_nova)
            db.session.commit()
            flash('feito')
        except:
            flash('seu email esta incorreto')
            return redirect(url_for('trocasenha'))
        return redirect(url_for('login'))
    return render_template("troca_senha.html")


if __name__ == "__main__":
    app.run()