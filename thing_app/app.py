from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
#from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import *
from flask_login import LoginManager 


app = Flask(__name__)
# auth = HTTPBasicAuth()

# users = {
    # "john": generate_password_hash("hello"),
    # "susan": generate_password_hash("bye")
# }

# @auth.verify_password
# def verify_password(username, password):
    # if username in users:
        # return check_password_hash(users.get(username), password)
    # return False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Sec123@localhost:3306/thing_db'

db = SQLAlchemy(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

class Pessoa(db.Model):

    __tablename__= 'cliente'

    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(10), unique=True, nullable=False, index=True)
    telefone = db.Column(db.String(120), unique=True, nullable=False)
    cpf = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    time = db.Column(db.DateTime, default=datetime.time)

    def __init__(self, nome, telefone, cpf, email, time):
        self.nome = nome
        self.telefone = telefone
        self.cpf = cpf
        self.email = email
        self.time = time

    db.create_all()
@app.route("/")
#@auth.login_required
def index():
    return render_template("index.html")

@app.route("/cadastrar")
def cadastrar():
    return render_template("cadastro.html")

@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        telefone = request.form.get("telefone")
        cpf = request.form.get("cpf")
        email = request.form.get("email")
        time = request.form.get("time")

        if nome and telefone and cpf and email and time:
            p = Pessoa(nome, telefone, cpf, email, time)
            db.session.add(p)
            db.session.commit()
            
    return redirect(url_for("index"))

@app.route("/lista")
def lista():
    pessoas = Pessoa.query.all()
    return render_template("lista.html", pessoas=pessoas)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user and not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)

    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user:
        flash('Email address already exists.')
        return redirect(url_for('auth.signup'))

    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))