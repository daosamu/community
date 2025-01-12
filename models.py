from flask_sqlalchemy import SQLAlchemy
import enum
from flask_login import UserMixin

db = SQLAlchemy()


# 定义用户角色枚举类
class UserRole(enum.Enum):
    USER = "普通用户"
    DOCTOR = "医生"
    ADMIN = "管理员"


# 用户模型类
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean, default=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    gender = db.Column(db.Enum("男", "女", "其他"))
    role = db.Column(db.Enum(UserRole), nullable=False)
    register_time = db.Column(db.DateTime)
    last_login_time = db.Column(db.DateTime)


# 分类模型类
class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), nullable=False)


# 文章模型类
class Article(db.Model):
    __tablename__ = "articles"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    publish_time = db.Column(db.DateTime)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)


# 问题模型类
class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    time = db.Column(db.DateTime)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)


# 评论模型类
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    comment_content = db.Column(db.Text, nullable=False)
    comment_time = db.Column(db.DateTime)
    comment_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id"))
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
    parent_comment_id = db.Column(db.Integer)


# 点赞模型类
class Like(db.Model):
    __tablename__ = "likes"
    id = db.Column(db.Integer, primary_key=True)
    like_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id"))
