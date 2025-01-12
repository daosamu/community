from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    TextAreaField,
    SelectField,
    IntegerField,
    DateTimeField,
    HiddenField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    ValidationError,
    Optional,
)
from models import User


# 自定义验证函数，检查用户名是否已存在
def validate_username(form, field):
    user = User.query.filter_by(username=field.data).first()
    if user and (not form.user_id.data or int(form.user_id.data) != user.id):
        raise ValidationError("用户名已存在，请选择其他用户名")


# 自定义验证函数，检查邮箱是否已存在
def validate_email(form, field):
    user = User.query.filter_by(email=field.data).first()
    if user and (not form.user_id.data or int(form.user_id.data) != user.id):
        raise ValidationError("该邮箱已被注册，请使用其他邮箱")


# 登录表单类
class LoginForm(FlaskForm):
    username = StringField("用户名", validators=[DataRequired()])
    password = PasswordField("密码", validators=[DataRequired()])
    submit = SubmitField("登录")


# 用户注册表单类
class RegistrationForm(FlaskForm):
    username = StringField(
        "用户名", validators=[DataRequired(), Length(min=4, max=20), validate_username]
    )
    password = PasswordField(
        "密码",
        validators=[
            DataRequired(),
            Length(min=8),
            EqualTo("confirm_password", message="两次密码必须一致"),
        ],
    )
    confirm_password = PasswordField("确认密码")
    email = StringField("邮箱", validators=[DataRequired(), Email(), validate_email])
    name = StringField("姓名", validators=[Optional(), Length(max=50)])
    age = IntegerField("年龄", validators=[Optional()])
    gender = SelectField(
        "性别",
        choices=[("男", "男"), ("女", "女"), ("其他", "其他")],
        validators=[Optional()],
    )
    submit = SubmitField("注册")


# 文章发布表单类
class ArticleForm(FlaskForm):
    title = StringField("文章标题", validators=[DataRequired(), Length(max=100)])
    content = TextAreaField("文章内容", validators=[DataRequired()])
    category_id = SelectField("文章分类", coerce=int, validators=[DataRequired()])
    submit = SubmitField("发布")


# 提问表单类
class QuestionForm(FlaskForm):
    title = StringField("问题标题", validators=[DataRequired(), Length(max=100)])
    content = TextAreaField("问题描述", validators=[DataRequired()])
    category_id = SelectField("问题分类", coerce=int, validators=[DataRequired()])
    tags = StringField("问题标签（多个标签用逗号分隔）", validators=[Optional()])
    submit = SubmitField("提问")


# 评论表单类
class CommentForm(FlaskForm):
    comment_content = TextAreaField("评论内容", validators=[DataRequired()])
    article_id = HiddenField("文章 ID")
    parent_comment_id = HiddenField("父评论 ID")
    submit = SubmitField("发表评论")
