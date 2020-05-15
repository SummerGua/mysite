from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, LoginManager, login_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from werkzeug.security import check_password_hash, generate_password_hash

# from forms import *
# from flask_wtf import FlaskForm
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from wtforms import StringField, SubmitField, PasswordField, BooleanField
# from wtforms.validators import DataRequired, Email, Length, EqualTo


app = Flask(__name__)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)

app.config["SECRET_KEY"] = '123456'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:gaga@localhost:3306/account'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)


class health(db.Model):
    __tablename__ = 'health'
    hospitalname = db.Column(db.String(40))
    date = db.Column(db.Date, nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('account.userid'))


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


@app.route('/index')
@app.route('/')  # route()函数是一个装饰器，它告诉应用程序哪个URL应该调用相关的函数。
def index():  # '/ ' URL与hello_world()函数绑定。因此，当在浏览器中打开web服务器的主页时，将呈现该函数的输出。
    return render_template('index.html')


@app.route('/adduser', methods=['POST', 'GET'])
# 注册
def adduser():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        u = User.query.filter(User.username == username).first()
        if u:
            flash('用户名已存在，请重新输入！')
            return redirect(url_for('index'))
        elif 2 < len(username.strip()) < 11 and 2 < len(password) < 13 and password == password2:
            userinfo = User()
            userinfo.username = username
            password = generate_password_hash(password)
            userinfo.password = password
            db.session.add(userinfo)
            db.session.commit()
            return redirect(url_for('go'))
        else:
            flash('用户名规定3到10个字符,密码规定3到12个字符,两次密码要相等，请重新输入！')
            return redirect(url_for('index'))
    return redirect(url_for('go'))


@app.route('/login', methods=['POST', 'GET'])
# 登录
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        u = User.query.filter(User.username == username).first()
        if u:  # 如果用户存在
            flag = check_password_hash(u.password, password)
            if flag:  # 登录成功
                login_user(u)
                # return render_template('userhome.html', username=username)
                return redirect(url_for('userhome'))
            else:  # 密码错误
                flash('密码错误')
                return redirect(url_for('go'))
        else:
            flash('账号不存在')
            return redirect(url_for('go'))
    return redirect(url_for('go'))


@app.route('/go')  # 点击注册页面的登录会来到login.html
def go():
    return render_template('login.html')


# @app.route('/userhome/<username>')
@login_required
def userhome(username):
    # user = User.query.filter(username == username).first()
    return render_template('userhome.html')


# db.create_all()
if __name__ == '__main__':
    app.run(debug=True)
