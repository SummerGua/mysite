from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired,EqualTo,Length


class RegisterForm(Form):
    username = StringField("用户名", validators=[DataRequired()])
    password = PasswordField("密码", validators=[DataRequired()])
    repassword = PasswordField("再次输入密码", validators=[EqualTo("password")])
    submid = SubmitField("确定")