from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, LoginManager, login_user, UserMixin, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.urls import url_parse

app = Flask(__name__)
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


class Weight(db.Model):
    __tablename__ = 'weight'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_name = db.Column(db.VARCHAR(20), db.ForeignKey('account.username'))
    date = db.Column(db.Date, nullable=False)
    weight = db.Column(db.DECIMAL(5, 2))


class Health(db.Model):
    __tablename__ = 'health'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    hospitalname = db.Column(db.String(40), nullable=False)
    date = db.Column(db.Date, nullable=False)
    details = db.Column(db.String(200), nullable=False)
    user_name = db.Column(db.VARCHAR(20), db.ForeignKey('account.username'))


class Bin(db.Model):
    __tablename__ = 'bin'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    hospitalname = db.Column(db.String(40), nullable=False)
    date = db.Column(db.Date, nullable=False)
    details = db.Column(db.String(200), nullable=False)
    user_name = db.Column(db.VARCHAR(20), db.ForeignKey('account.username'))


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/index')
@app.route('/')  # route()函数是一个装饰器，它告诉应用程序哪个URL应该调用相关的函数。
def index():  # '/ ' URL与hello_world()函数绑定。因此，当在浏览器中打开web服务器的主页时，将呈现该函数的输出。
    return render_template('index.html')


@app.route('/go')  # 点击注册页面的登录会来到login.html
def go():
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/delete_info/<info_id>')
@login_required
def delete_info(info_id):
    to_delete_info = Health.query.get(info_id)
    to_bin_info = Health.query.filter(Health.id == info_id).first()
    if to_delete_info:
        bin_info = Bin()
        bin_info.user_name = to_bin_info.user_name
        bin_info.hospitalname = to_bin_info.hospitalname
        bin_info.date = to_bin_info.date
        bin_info.details = to_bin_info.details
        bin_info.id = to_bin_info.id
        db.session.add(bin_info)
        db.session.commit()
        db.session.delete(to_delete_info)
        db.session.commit()
        return redirect(url_for('userhome', username=current_user.username))


@app.route('/delbin<info_id>')
@login_required
def delbin(info_id):
    info = Bin.query.get(info_id)
    if info:
        db.session.delete(info)
        db.session.commit()
        return redirect(url_for('rubbish', username=current_user.username))


@app.route('/delweight<wei_id>')
@login_required
def delweight(wei_id):
    wei = Weight.query.get(wei_id)
    if wei:
        db.session.delete(wei)
        db.session.commit()
        return redirect(url_for('userhome', username=current_user.username))
    return redirect(url_for('userhome', username=current_user.username))


@app.route('/recover/<info_id>')
@login_required
def recover(info_id):
    info = Bin.query.get(info_id)
    info2 = Bin.query.filter(Bin.id == info_id).first()
    if info:
        reinfo = Health()
        reinfo.id = info2.id
        reinfo.date = info2.date
        reinfo.details = info2.details
        reinfo.hospitalname = info2.hospitalname
        reinfo.user_name = info.user_name
        db.session.add(reinfo)
        db.session.commit()
        db.session.delete(info)
        db.session.commit()
        return redirect(url_for('rubbish', username=current_user.username))


# 回收站页面
@app.route('/rubbish/<username>')
@login_required
def rubbish(username):
    userinfo = Bin.query.filter(Bin.user_name == username).all()
    return render_template('rubbish.html', bin_info=userinfo)


@app.route('/userhome/<username>')
@login_required
def userhome(username):
    userinfo = Health.query.filter(Health.user_name == username).all()
    weightinfo = Weight.query.filter(Weight.user_name == username).order_by(Weight.date).all()
    return render_template('userhome.html', info=userinfo, weight=weightinfo)


@app.route('/addweight', methods=['POST', 'GET'])
@login_required
def addweight():
    if request.method == 'POST':
        date = request.form.get('wdate')
        weight = request.form.get('weight')
        if len(date) > 0 and len(weight) > 0:
            weightinfo = Weight()
            weightinfo.date = date
            weightinfo.weight = weight
            weightinfo.user_name = current_user.username
            db.session.add(weightinfo)
            db.session.commit()
            return redirect(url_for('userhome', username=current_user.username))
        return redirect(url_for('userhome', username=current_user.username))
    return redirect(url_for('userhome', username=current_user.username))


@app.route('/update', methods=['POST', 'GET'])
@login_required
def update():
    if request.method == 'POST':
        hospital_name = request.form.get('hospitalname')
        date = request.form.get('date')
        details = request.form.get('details')
        healthinfo = Health()
        healthinfo.hospitalname = hospital_name
        healthinfo.date = date
        healthinfo.user_name = current_user.username
        healthinfo.details = details
        db.session.add(healthinfo)
        db.session.commit()
        return redirect(url_for('userhome', username=current_user.username))


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
                next_page = request.args.get('next')
                print(next_page)
                if not next_page or url_parse(next_page).netloc != '':  # 解析URL不为空
                    next_page = url_for('userhome', username=current_user.username)
                return redirect(next_page)
            else:  # 密码错误
                flash(u'密码错误')
                return redirect(url_for('go'))
        else:
            flash(u'账号不存在')
            return redirect(url_for('go'))
    return redirect(url_for('go'))


db.create_all()  # 用数据模型创建数据库时使用
if __name__ == '__main__':
    app.run(debug=True)
