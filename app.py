from flask import Flask, render_template, request, redirect, url_for, flash
from models import (
    db,
    UserRole,
    Question,
    User,
    Article,
    Category,
    Comment,
    Like,
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    current_user,
    login_required,
)
import datetime
from forms import (
    LoginForm,
    RegistrationForm,
    ArticleForm,
    QuestionForm,
    CommentForm,
)
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config["SECRET_KEY"] = "123456"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///community.db"
db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # 获取最新的文章
    articles = Article.query.order_by(Article.publish_time.desc()).limit(1).all()
    categories = Category.query.all()
    # 获取最新的提问
    questions = Question.query.order_by(Question.time.desc()).limit(1).all()
    return render_template(
        "index.html",
        articles=articles,
        categories=categories,
        questions=questions,
        User=User,
        UserRole=UserRole,
        current_user=current_user,  # 传递当前用户对象
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data,
            password=hashed_password,
            email=form.email.data,
            name=form.name.data,
            age=form.age.data,
            gender=form.gender.data,
            role=UserRole.USER,
            register_time=datetime.datetime.now(),
        )
        db.session.add(user)
        db.session.commit()
        flash("注册成功，请登录")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("登录成功")
            return redirect(url_for("index"))
        else:
            flash("用户名或密码错误")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("已退出登录")
    return redirect(url_for("index"))


@app.route("/article/new", methods=["GET", "POST"])
@login_required
def new_article():
    if current_user.role == UserRole.USER:
        flash("您没有权限发布文章")
        return redirect(url_for("article_list"))
    form = ArticleForm()
    form.category_id.choices = [
        (category.id, category.category_name) for category in Category.query.all()
    ]
    if form.validate_on_submit():
        tags = form.tags.data.split(",") if form.tags.data else []
        article = Article(
            title=form.title.data,
            content=form.content.data,
            publish_time=datetime.datetime.now(),
            author_id=current_user.id,
            category_id=form.category_id.data,
        )
        db.session.add(article)
        db.session.commit()
        db.session.commit()
        flash("文章发布成功")
        return redirect(url_for("article_list"))
    return render_template(
        "new_article.html",
        form=form,
        UserRole=UserRole,
    )


@app.route("/question/new", methods=["GET", "POST"])
@login_required
def new_question():
    form = QuestionForm()
    # 为category_id字段设置选项，从数据库中获取所有分类信息来填充
    form.category_id.choices = [
        (category.id, category.category_name) for category in Category.query.all()
    ]
    if form.validate_on_submit():
        question = Question(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id,
            time=datetime.datetime.now(),
        )
        db.session.add(question)
        db.session.commit()
        flash("提问成功")
        return redirect(url_for("question_list"))
    return render_template(
        "new_question.html",
        form=form,
        UserRole=UserRole,
    )


@app.route("/article/<int:article_id>", methods=["GET", "POST"])
def article_detail(article_id):
    article = Article.query.get(article_id)
    comments = Comment.query.filter_by(article_id=article_id).all()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            comment_content=form.comment_content.data,
            comment_time=datetime.datetime.now(),
            comment_user_id=current_user.id,
            article_id=article_id,
            parent_comment_id=form.parent_comment_id.data,
        )
        db.session.add(comment)
        db.session.commit()
        flash("评论发表成功")
        return redirect(url_for("article_detail", article_id=article_id))
    return render_template(
        "article_detail.html",
        article=article,
        comments=comments,
        form=form,
        User=User,
        UserRole=UserRole,
    )


@app.route("/question/<int:question_id>", methods=["GET", "POST"])
def question_detail(question_id):
    question = Question.query.get(question_id)
    comments = Comment.query.filter_by(question_id=question_id).all()
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(
            comment_content=form.comment_content.data,
            comment_time=datetime.datetime.now(),
            comment_user_id=current_user.id,
            question_id=question_id,
            parent_comment_id=form.parent_comment_id.data,
        )
        db.session.add(new_comment)
        db.session.commit()
        flash("评论发表成功")
        return redirect(url_for("question_detail", question_id=question_id))
    return render_template(
        "question_detail.html",
        question=question,
        comments=comments,
        form=form,
        User=User,
        UserRole=UserRole,
    )


@app.route("/like/<int:article_id>", methods=["GET", "POST"])
@login_required
def like_article(article_id):
    article = Article.query.get(article_id)
    like = Like.query.filter_by(
        like_user_id=current_user.id, article_id=article_id
    ).first()
    if like:
        db.session.delete(like)
        article.likes -= 1
    else:
        new_like = Like(like_user_id=current_user.id, article_id=article_id)
        db.session.add(new_like)
        article.likes += 1
    db.session.commit()
    return redirect(url_for("article_detail", article_id=article_id))


@app.route("/article_list", methods=["GET"])
@login_required
def article_list():
    articles = Article.query.all()
    categories = Category.query.all()
    author_ids = [article.author_id for article in articles]
    authors = {
        user.id: user.username
        for user in User.query.filter(User.id.in_(author_ids)).all()
    }
    return render_template(
        "article_list.html",
        articles=articles,
        categories=categories,
        User=User,
        authors=authors,
        UserRole=UserRole,
    )


@app.route("/question_list", methods=["GET"])
@login_required
def question_list():
    questions = Question.query.all()
    categories = Category.query.all()
    user_ids = [question.user_id for question in questions]
    users = {
        user.id: user.username
        for user in User.query.filter(User.id.in_(user_ids)).all()
    }
    return render_template(
        "question_list.html",
        questions=questions,
        categories=categories,
        users=users,
        User=User,
        UserRole=UserRole,
    )


@app.route("/filter_articles_by_category", methods=["POST"])
@login_required
def filter_articles_by_category():
    category_id = request.form.get("category_id")
    if category_id:
        filtered_articles = Article.query.filter_by(category_id=category_id).all()
        categories = Category.query.all()  # 获取所有分类信息
        author_ids = [article.author_id for article in filtered_articles]
        authors = {
            user.id: user.username
            for user in User.query.filter(User.id.in_(author_ids)).all()
        }
        return render_template(
            "filtered_article_list.html",
            articles=filtered_articles,
            categories=categories,
            User=User,
            authors=authors,
            UserRole=UserRole,
        )
    else:
        flash("未获取到有效的分类ID，请重新操作")
        return redirect(url_for("article_list"))


@app.route("/filter_questions_by_category", methods=["POST"])
@login_required
def filter_questions_by_category():
    category_id = request.form.get("category_id")
    if category_id:
        filtered_questions = Question.query.filter_by(category_id=category_id).all()
        categories = (
            Category.query.all()
        )  # 获取所有分类信息，方便在模板中展示分类下拉框等元素
        user_ids = [question.user_id for question in filtered_questions]
        users = {
            user.id: user.username
            for user in User.query.filter(User.id.in_(user_ids)).all()
        }
        return render_template(
            "filtered_question_list.html",
            questions=filtered_questions,  # 此处变量名修改为 questions，与模板中的循环变量对应一致
            categories=categories,
            users=users,
            User=User,
            UserRole=UserRole,
        )
    else:
        flash("未获取到有效的分类ID，请重新操作")
        return redirect(url_for("question_list"))


# 管理员用户管理页面路由，展示所有用户列表
@app.route("/admin/user_management", methods=["GET"])
@login_required
def user_management():
    users = User.query.all()
    return render_template(
        "user_management.html",
        users=users,
        UserRole=UserRole,
    )


# 根据用户ID删除用户的路由
@app.route("/admin/delete_user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash(f"用户 {user.username} 已成功删除")
    else:
        flash(f"未找到ID为 {user_id} 的用户，删除失败")
    return redirect(url_for("user_management"))


# 修改用户角色的路由
@app.route("/admin/modify_user_role/<int:user_id>", methods=["POST"])
@login_required
def modify_user_role(user_id):
    new_role = request.form.get("new_role")  # 从表单中获取新的角色值
    user = User.query.get(user_id)
    if user and new_role in [role.value for role in UserRole]:
        user.role = UserRole(new_role)
        db.session.commit()
        flash(f"用户 {user.username} 的角色已修改为 {new_role}")
    else:
        flash("修改用户角色失败，请检查用户是否存在及角色值是否合法")
    return redirect(url_for("user_management"))


# 根据角色筛选用户路由
@app.route("/admin/filter_users_by_role", methods=["POST"])
@login_required
def filter_users_by_role():
    role_filter = request.form.get("role_filter")
    if role_filter == "医生":
        filtered_users = User.query.filter(User.role == UserRole.DOCTOR).all()
    elif role_filter == "普通用户":
        filtered_users = User.query.filter(User.role == UserRole.USER).all()
    else:
        filtered_users = User.query.all()
    return render_template(
        "filter_users_by_role.html", users=filtered_users, UserRole=UserRole
    )


# 新增用户表单处理路由（普通用户）
@app.route("/admin/add_user_user", methods=["GET", "POST"])
@login_required
def add_user_user():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data,
            password=hashed_password,
            email=form.email.data,
            name=form.name.data,
            age=form.age.data,
            gender=form.gender.data,
            role=UserRole.USER,
            register_time=datetime.datetime.now(),
        )
        db.session.add(user)
        db.session.commit()
        flash("普通用户添加成功")
        return redirect(url_for("user_management"))
    return render_template("add_user_user.html", form=form, UserRole=UserRole)


# 新增用户表单处理路由（医生）
@app.route("/admin/add_user_doctor", methods=["GET", "POST"])
@login_required
def add_user_doctor():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data,
            password=hashed_password,
            email=form.email.data,
            name=form.name.data,
            age=form.age.data,
            gender=form.gender.data,
            role=UserRole.DOCTOR,
            register_time=datetime.datetime.now(),
        )
        db.session.add(user)
        db.session.commit()
        flash("医生用户添加成功")
        return redirect(url_for("user_management"))
    return render_template("add_user_doctor.html", form=form, UserRole=UserRole)


# 新增用户表单处理路由（管理员）
@app.route("/admin/add_user_admin", methods=["GET", "POST"])
@login_required
def add_user_admin():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data,
            password=hashed_password,
            email=form.email.data,
            name=form.name.data,
            age=form.age.data,
            gender=form.gender.data,
            role=UserRole.ADMIN,
            register_time=datetime.datetime.now(),
        )
        db.session.add(user)
        db.session.commit()
        flash("管理员用户添加成功")
        return redirect(url_for("user_management"))
    return render_template("add_user_admin.html", form=form, UserRole=UserRole)


# 通过id查找用户路由
@app.route("/admin/find_user_by_id", methods=["GET", "POST"])
@login_required
def find_user_by_id():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        if user_id:
            user = User.query.get(int(user_id))
            if user:
                return render_template("user_detail.html", user=user)
            else:
                flash("未找到对应ID的用户")
        else:
            flash("请输入有效的用户ID")
    return render_template("find_user_by_id.html")


@app.route("/article_list/search", methods=["POST"])
@login_required
def article_list_search():
    search_keyword = request.form.get("search_keyword")
    if search_keyword:
        # 使用模糊查询来匹配文章标题或者文章内容包含关键字的文章
        # 这里假设使用SQLAlchemy的 `like` 操作符来实现模糊查询
        filtered_articles = Article.query.filter(
            (Article.title.like(f"%{search_keyword}%"))
            | (Article.content.like(f"%{search_keyword}%"))
        ).all()
        categories = Category.query.all()
        author_ids = [article.author_id for article in filtered_articles]
        authors = {
            user.id: user.username
            for user in User.query.filter(User.id.in_(author_ids)).all()
        }
        return render_template(
            "article_list.html",
            articles=filtered_articles,
            categories=categories,
            User=User,
            authors=authors,
            UserRole=UserRole,
        )
    else:
        flash("请输入有效的查询关键字")
        return redirect(url_for("article_list"))


@app.route("/question_list/search", methods=["POST"])
@login_required
def question_list_search():
    search_keyword = request.form.get("search_keyword")
    if search_keyword:
        # 使用模糊查询来匹配问题标题或者问题内容包含关键字的文章
        # 这里假设使用SQLAlchemy的 `like` 操作符来实现模糊查询
        filtered_questions = Question.query.filter(
            (Question.title.like(f"%{search_keyword}%"))
            | (Question.content.like(f"%{search_keyword}%"))
        ).all()
        categories = Category.query.all()
        user_ids = [question.user_id for question in filtered_questions]
        users = {
            user.id: user.username
            for user in User.query.filter(User.id.in_(user_ids)).all()
        }
        return render_template(
            "question_list.html",
            questions=filtered_questions,
            categories=categories,
            users=users,
            User=User,
            UserRole=UserRole,
        )
    else:
        flash("请输入有效的查询关键字")
        return redirect(url_for("question_list"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
