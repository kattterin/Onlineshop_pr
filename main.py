from flask import Flask, render_template, redirect, request, make_response, session, abort, jsonify
from data import db_session
from data.users import User
from data.goods import Goods
from data.category import Category
from data.brand import Brand
from wtforms import SubmitField
from forms.loginform import LoginForm
from forms.user import RegisterForm
from forms.goodsform import GoodForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="Главная")


@app.route("/show_goods")
def show_goods():
    db_sess = db_session.create_session()
    goods = db_sess.query(Goods)
    return render_template("all_goods.html", title="Товары", goods=goods)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/good', methods=['GET', 'POST'])
@login_required
def new_good():
    form = GoodForm()
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    brandies = db_sess.query(Brand).all()

    form.category.choices = [(i.id, i.name) for i in categories]
    form.brand.choices = [(i.id, i.name) for i in brandies]

    if form.validate_on_submit():
        goods = Goods()
        goods.title = form.title.data
        goods.content = form.content.data
        # goods.is_private = form.is_private.data
        goods.slug = form.slug.data
        goods.price = float(form.price.data)
        goods.old_price = float(form.old_price.data)
        goods.categories.extend(db_sess.query(Category).filter(Category.id.in_(form.category.data)).all())
        goods.brandies.append(db_sess.query(Brand).all()[form.brand.data])
        # current_user.news.append(news)
        # db_sess.merge(current_user)
        db_sess.merge(goods)

        db_sess.commit()
        return redirect('/show_goods')

    return render_template('good.html', title='Добавление новости',
                           form=form)


@app.route('/good_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def good_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(Goods).filter(Goods.id == id).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/good/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_good(id):
    form = GoodForm()

    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    brandies = db_sess.query(Brand).all()
    form.category.choices = [(i.id, i.name) for i in categories]
    form.brand.choices = [(i.id, i.name) for i in brandies]
    if request.method == "GET":
        goods = db_sess.query(Goods).filter(Goods.id == id).first()
        if goods:

            form.title.data = goods.title
            form.content.data = goods.content
            form.slug.data = goods.slug
            form.price.data = goods.price
            form.old_price.data = goods.old_price
            form.category.data = [i.id for i in goods.categories]
            form.brand.data = [i.id for i in goods.brandies][0] if [i.id for i in goods.brandies] else None
        else:
            abort(404)
    if form.validate_on_submit():
        goods = db_sess.query(Goods).filter(Goods.id == id).first()
        if goods:
            goods.title = form.title.data
            goods.content = form.content.data
            goods.slug = form.slug.data
            goods.price = float(form.price.data)
            goods.old_price = float(form.old_price.data)
            goods.categories = []
            goods.categories.extend(db_sess.query(Category).filter(Category.id.in_(form.category.data)).all())
            goods.brandies = []
            goods.brandies.append(db_sess.query(Brand).all()[form.brand.data])
            db_sess.commit()
            return redirect('/show_goods')
        else:
            abort(404)
    return render_template('good.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/cart/add_default/<int:id>', methods=['GET', 'POST'])
@login_required
def addgoodinb(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == current_user.email).first()
    print(user.basket)
    good = db_sess.query(Goods).filter(Goods.id == id).first()
    print(good.id)


# @app.route('/basket/<int:id>', methods=['GET', 'POST'])
# @login_required
# def basket(id):
# db_sess = db_session.create_session()
# user = db_sess.query(User).filter(User.email == current_user.email).first()
# print(user.basket)
# good = db_sess.query(Goods).filter(Goods.id == id).first()
# print(good.id)
# return redirect("/show_goods")
# form = LoginForm()
# if form.validate_on_submit():
#     db_sess = db_session.create_session()
#     user = db_sess.query(User).filter(User.email == form.email.data).first()
#     if user and user.check_password(form.password.data):
#         login_user(user, remember=form.remember_me.data)
#         return redirect("/")
#     return render_template('login.html',
#                            message="Неправильный логин или пароль",
#                            form=form)

# return render_template('basket.html', title='Корзина', dict_product=dict_product)


def main():
    db_session.global_init("db/shop.sqlite3")
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
