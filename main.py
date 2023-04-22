import os
import json
from flask import Flask, render_template, redirect, request, make_response, session, abort, jsonify, url_for
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
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
app.config['UPLOAD_FOLDER'] = 'uploads'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, int(user_id))


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="Главная")


@app.route('/drop_down1', methods=['GET', 'POST'])
def drop_down():
    sime = ['df', 'efew']
    return redirect(url_for('show_goods', sime=sime))


@app.route("/show_goods", methods=['GET', 'POST'])
def show_goods():
    global prom_good, prom_query, prom_mycheckboxes
    db_sess = db_session.create_session()
    categories = {i.name: i.id for i in db_sess.query(Category)}  # список категорий
    button_pressed = 'check_click' in request.form
    if button_pressed or request.url != request.referrer:
        query = request.args.get('query')
        mycheckboxes = request.form.getlist('mycheckboxes')

        cat = [i for i in db_sess.query(Category) if i.name in mycheckboxes]
        if cat:
            all_product = set(([j.id for j in cat[0].goods]))
            for i in cat[1:]:
                all_product = all_product.intersection(set([j.id for j in i.goods]))
            all_product = list(all_product)
            if query:
                goods = db_sess.query(Goods).filter(Goods.id.in_(all_product), Goods.title.like(f'%{query}%'))
            else:
                goods = db_sess.query(Goods).filter(Goods.id.in_(all_product))
        else:
            if query:
                goods = db_sess.query(Goods).filter(Goods.title.like(f'%{query}%'))
            else:
                goods = db_sess.query(Goods)
        prom_good = goods
        prom_query = query
        prom_mycheckboxes = mycheckboxes
        return render_template("all_goods.html", title="Товары", goods=goods, categories=categories.keys(),
                               mycheckboxes=mycheckboxes, sear=query)
    else:
        return render_template("all_goods.html", title="Товары", goods=prom_good, categories=categories.keys(),
                               mycheckboxes=prom_mycheckboxes, sear=prom_query)


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
        # file = request.files['image']
        goods = Goods()
        goods.title = form.title.data
        goods.content = form.content.data
        # goods.is_private = form.is_private.data
        goods.slug = form.slug.data
        goods.price = float(form.price.data)
        goods.old_price = float(form.old_price.data)
        goods.categories.extend(db_sess.query(Category).filter(Category.id.in_(form.category.data)).all())
        goods.brandies.append(db_sess.query(Brand)[form.brand.data])
        # if file:
        #     filename = file.filename
        #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #     file = form.image.data
        #     goods.image = file.read()
        # current_user.news.append(news)
        # db_sess.merge(current_user)
        goods.user = current_user

        db_sess.merge(goods)

        db_sess.commit()
        return redirect('/show_goods')

    return render_template('good.html', title='Добавление новости',
                           form=form)


@app.route('/good_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def good_delete(id):
    db_sess = db_session.create_session()
    good = db_sess.query(Goods).filter(Goods.id == id).first()
    if good:
        db_sess.delete(good)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/show_goods')


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
            print(form.brand.data)
            goods.brandies.append(db_sess.query(Brand)[form.brand.data])
            db_sess.commit()
            return redirect('/show_goods')
        else:
            abort(404)
    return render_template('good.html',
                           title='Редактирование товара',
                           form=form
                           )


@app.route('/basket', methods=['GET', 'POST'])
@login_required
def basket():
    db_sess = db_session.create_session()

    # получение объекта модели для изменения
    user = db_sess.query(User).filter(User.email == current_user.email).first()
    korzina1 = json.loads(user.basket) if user.basket else {}
    korzina_g = [int(i) for i in korzina1.keys()]
    goods = db_sess.query(Goods).filter(Goods.id.in_(korzina_g))
    return render_template("basket.html", title="Корзина", goods=goods)


@app.route('/korzina/<int:id_>', methods=['GET', 'POST'])
@login_required
def korzina(id_):
    db_sess = db_session.create_session()
    categories = [i.name for i in db_sess.query(Category)]
    # получение объекта модели для изменения
    user = db_sess.query(User).filter(User.email == current_user.email).first()
    korzina = json.loads(user.basket) if user.basket else {}
    # if korzina:
    if not korzina.get(id_):
        korzina[str(id_)] = 1
        user.basket = {}
        user.basket = json.dumps(korzina)
        db_sess.commit()
    return redirect(url_for('show_goods'))


@app.route('/good_delete_from_b/<int:id_>', methods=['GET', 'POST'])
@login_required
def good_delete_from_b(id_):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == current_user.email).first()
    korzina = json.loads(user.basket) if user.basket else {}
    if korzina:
        korzina.pop(str(id_))
        user.basket = {}
        user.basket = json.dumps(korzina)
        db_sess.commit()
    return redirect('/basket')


@app.route('/all_users')
def all_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).filter(User.email != current_user.email).all()
    return render_template('all_users.html', users=users)


@app.route('/user_delete/<int:id_>', methods=['GET', 'POST'])
@login_required
def user_delete(id_):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id_).first()
    goods = db_sess.query(Goods).filter(Goods.user_id == id_)

    if user:
        db_sess.delete(user)
        for i in goods:
            db_sess.delete(i)
        db_sess.commit()

    else:
        abort(404)
    return redirect('/all_users')


@app.route('/user_change/<int:id_>', methods=['GET', 'POST'])
@login_required
def user_change(id_):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id_).first()
    if user:
        user.is_seller = 0 if user.is_seller else 1
        if not user.is_seller:
            goods = db_sess.query(Goods).filter(Goods.user_id == id_)
            for i in goods:
                db_sess.delete(i)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/all_users')


def main():
    db_session.global_init("db/shop.sqlite3")
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
