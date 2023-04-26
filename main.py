import os
import json
from flask import Flask, render_template, redirect, request, make_response, session, abort, jsonify, url_for, flash, \
    send_file, Response
from flask_restful import Api

from data import db_session, goods_resources
from data.users import User
from data.cart import Cart

from data.goods import Goods
from data.category import Category
from io import BytesIO
from base64 import b64encode
from forms.loginform import LoginForm
from forms.user import RegisterForm
from forms.goodsform import GoodForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import asc, desc

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = os.urandom(32)
app.config['UPLOAD_FOLDER'] = 'uploads'
login_manager = LoginManager()
login_manager.init_app(app)
api.add_resource(goods_resources.GoodsListResource, '/api/good')

api.add_resource(goods_resources.GoodsResource, '/api/good/<int:goods_id>')


@app.errorhandler(404)
def page_not_found(error):
    error_code = 404
    error_message = "Страница не найдена"
    error_description = "Запрашиваемая страница не существует. Проверьте правильность URL-адреса."
    return render_template('error.html', error_code=error_code, error_message=error_message,
                           error_description=error_description), 404


@app.errorhandler(500)
def serv_error(error):
    error_code = 500
    error_message = "Ошибка сервера"
    error_description = "Извините, произошла внутренняя ошибка сервера, мы работаем над ее исправлением."
    return render_template('error.html', error_code=error_code, error_message=error_message,
                           error_description=error_description), 500


@app.errorhandler(403)
def forbidden(error):
    error_code = 403
    error_message = "Ошибка доступа к странице"
    error_description = "К сожалению, у вас нет доступа к запрашиваемой странице."
    return render_template('error.html', error_code=error_code, error_message=error_message,
                           error_description=error_description), 403


@app.errorhandler(401)
def authoriz(error):
    error_code = 401
    error_message = "Ошибка авторизации"
    error_description = "Для доступа к этой странице необходимо авторизоваться."
    return render_template('error.html', error_code=error_code, error_message=error_message,
                           error_description=error_description), 401


@app.errorhandler(400)
def Badrequest(error):
    error_code = 400
    error_message = "Ошибка запрос"
    error_description = "К сожалению, ваш запрос содержит некорректные данные. Попробуйте изменить параметры запроса."
    return render_template('error.html', error_code=error_code, error_message=error_message,
                           error_description=error_description), 400


@app.errorhandler(405)
def method_not_allow(error):
    error_code = 405
    error_message = "Метод не используется на сервере"
    error_description = "К сожалению, метод HTTP, который вы используете в запросе, не поддерживается на сервере."
    return render_template('error.html', error_code=error_code, error_message=error_message,
                           error_description=error_description), 405


@app.errorhandler(400)
def Serviceunavailable(error):
    error_code = 400
    error_message = "Cервер временно недоступен"
    error_description = "Извините, сервер временно недоступен из-за технических проблем или перегрузки. Попробуйте повторить запрос позже."
    return render_template('error.html', error_code=error_code, error_message=error_message,
                           error_description=error_description), 400


def image_to_html(img):
    a = BytesIO(img.read())
    img_data = a.getvalue()
    img_base64 = b64encode(img_data).decode('utf-8')
    return img_base64


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, int(user_id))


@app.route('/update_quantity/<int:id_>', methods=['POST'])
def update_quantity(id_):
    """изменение количества товара в базе данных"""
    quantity = request.form['quantity']
    db_sess = db_session.create_session()
    # получение объекта модели для изменения
    cart = db_sess.query(Cart).filter(Cart.user_id == current_user.id, Cart.goods_id == id_).first()
    cart.amount = quantity
    cart.total = int((db_sess.query(Goods.price).filter(Goods.id == id_).first())[0]) * int(cart.amount)
    db_sess.commit()
    if 'basket' in request.referrer:
        return redirect(url_for('basket'))
    return redirect(url_for('show_goods'))


sort_ = 1


@app.route("/index", methods=['GET', 'POST'])
@app.route("/show_goods", methods=['GET', 'POST'])
@app.route("/", methods=['GET', 'POST'])
def show_goods():
    global prom_good, prom_query, prom_mycheckboxes, sort_
    # sort_btn = request.files['sort_desc'] if request.files.get('sort_desc') else request.files['sort_asc']
    db_sess = db_session.create_session()
    categories = db_sess.query(Category)  # список категорий
    button_pressed = 'check_click' in request.form
    users_cart = {i.goods_id: i.amount for i in db_sess.query(Cart).filter(
        Cart.user_id == current_user.id).all()} if current_user.is_authenticated else {}
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
                goods = db_sess.query(Goods).filter(Goods.id.in_(all_product), Goods.title.ilike(f'%{query.lower()}%'))
            else:
                goods = db_sess.query(Goods).filter(Goods.id.in_(all_product))
        else:
            if query:
                goods = db_sess.query(Goods).filter(Goods.title.ilike(f'%{query.lower()}%'))
            else:
                goods = db_sess.query(Goods)
        if 'sort_asc' in request.form:
            goods = goods.order_by(Goods.price.asc())
        elif 'sort_desc' in request.form:
            goods = goods.order_by(Goods.price.desc())
        if 'bars' in request.form:
            sort_ = False
        elif 'ellipsis' in request.form:
            sort_ = True

        prom_good = goods
        prom_query = query
        prom_mycheckboxes = mycheckboxes
        return render_template("all_goods.html", title="Главная", goods=goods, categories=categories,
                               mycheckboxes=mycheckboxes, sear=query, users_cart=users_cart, sort_=sort_)
    else:
        if 'bars' in request.form:
            sort_ = False
        elif 'ellipsis' in request.form:
            sort_ = True
        if 'sort_asc' in request.form:
            return render_template("all_goods.html", title="Главная", goods=prom_good.order_by(Goods.price.asc()),
                                   categories=categories,
                                   mycheckboxes=prom_mycheckboxes, sear=prom_query, users_cart=users_cart, sort_=sort_)
        elif 'sort_desc' in request.form:
            return render_template("all_goods.html", title="Главная", goods=prom_good.order_by(Goods.price.desc()),
                                   categories=categories,
                                   mycheckboxes=prom_mycheckboxes, sear=prom_query, users_cart=users_cart, sort_=sort_)
        return render_template("all_goods.html", title="Главная", goods=prom_good, categories=categories,
                               mycheckboxes=prom_mycheckboxes, sear=prom_query, users_cart=users_cart, sort_=sort_)


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
        if db_sess.query(User).filter(User.phone == form.phone.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Данный номер уже зарегистрирован")
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
    form.category.choices = [(i.id, i.name) for i in categories]
    image = image_to_html(request.files['img']) if request.files.get('img') else ''
    if form.validate_on_submit():
        # file = request.files['image']
        goods = Goods()
        goods.title = form.title.data
        goods.content = form.content.data
        # goods.is_private = form.is_private.data
        goods.price = form.price.data
        goods.old_price = form.old_price.data
        goods.categories.extend(db_sess.query(Category).filter(Category.id.in_(form.category.data)).all())
        goods.discount = int(-1 * ((int(form.price.data) / int(form.old_price.data)) * 100 - 100))
        goods.in_stock = form.in_stock.data
        if image:
            goods.image = image
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
    return render_template('good.html', title='Добавление товара',
                           form=form, image=image)


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


@app.route('/good/<int:id_>', methods=['GET', 'POST'])
@login_required
def edit_good(id_):
    form = GoodForm()
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    form.category.choices = [(i.id, i.name) for i in categories]
    image = ''
    if request.files.get('img'):
        image = image_to_html(request.files['img'])
    if request.method == "GET":
        goods = db_sess.query(Goods).filter(Goods.id == id_).first()
        if goods:

            form.title.data = goods.title
            form.content.data = goods.content
            form.price.data = goods.price
            form.old_price.data = goods.old_price
            form.category.data = [i.id for i in goods.categories]
            form.in_stock.data = goods.in_stock
            image = goods.image
        else:
            abort(404)
    if form.validate_on_submit():
        goods = db_sess.query(Goods).filter(Goods.id == id_).first()
        if goods:
            goods.title = form.title.data
            goods.content = form.content.data
            goods.price = int(form.price.data)
            goods.discount = int(-1 * ((int(form.price.data) / int(form.old_price.data)) * 100 - 100))
            goods.old_price = int(form.old_price.data)
            goods.in_stock = form.in_stock.data
            goods.categories = []
            goods.categories.extend(db_sess.query(Category).filter(Category.id.in_(form.category.data)).all())

            if image:
                goods.image = image
            db_sess.commit()
            return redirect('/show_goods')
        else:
            abort(404)

    # return f'<img src="data:image/jpeg;base64,{data}" alt="{image.name}">'
    return render_template('good.html',
                           title='Редактирование товара',
                           form=form, image=image
                           )


@app.route('/basket', methods=['GET', 'POST'])
@login_required
def basket():
    db_sess = db_session.create_session()
    cart = db_sess.query(Cart)
    for i in cart:
        g_p = (db_sess.query(Goods).filter(Goods.id == i.goods_id).first())
        if i.amount > g_p.in_stock:
            i.amount = g_p.in_stock
        i.total = int(g_p.price) * int(i.amount)
    db_sess.commit()

    # получение объекта модели для изменения
    korz = db_sess.query(Cart.goods_id).filter(Cart.user_id == current_user.id)
    goods = db_sess.query(Goods).filter(Goods.id.in_(korz))
    users_cart = {i.goods_id: [i.amount, i.total] for i in db_sess.query(Cart).filter(
        Cart.user_id == current_user.id).all()} if current_user.is_authenticated else {}
    all_total = sum([int(i[1]) for i in users_cart.values() if i[0] > 0])
    return render_template("basket.html", title="Корзина", goods=goods, users_cart=users_cart, all_total=all_total)


@app.route('/korzina/<int:id_>', methods=['GET', 'POST'])
@login_required
def korzina(id_):
    db_sess = db_session.create_session()
    # получение объекта модели для изменения
    korz = db_sess.query(Cart).filter(Cart.user_id == current_user.id, Cart.goods_id == id_).first()
    # if korzina:
    if not korz:
        cart = Cart()
        cart.user_id = current_user.id
        cart.goods_id = id_
        prod = db_sess.query(Goods).filter(Goods.id == id_).first()
        cart.amount = 1 if prod.in_stock > 0 else 0
        cart.total = int(prod.price) * int(cart.amount)
        db_sess.add(cart)
        db_sess.commit()
    return redirect(url_for('show_goods'))


@app.route('/good_delete_from_b/<int:id_>', methods=['GET', 'POST'])
@login_required
def good_delete_from_b(id_):
    db_sess = db_session.create_session()
    korz = db_sess.query(Cart).filter(Cart.user_id == current_user.id, Cart.goods_id == id_).first()
    if korz:
        db_sess.delete(korz)
        db_sess.commit()

    return redirect('/basket')


@app.route('/all_users')
def all_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).filter(User.email != current_user.email).all()
    return render_template('all_users.html', users=users, title="Все пользователи")


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


@app.route('/somenew', methods=['GET', 'POST'])
@login_required
def somenew():
    """новая категория"""
    cat_name = request.form.get('cat_name')
    db_sess = db_session.create_session()
    cat = db_sess.query(Category)
    if not cat_name.lower() in [i.name.lower() for i in cat] and cat_name:
        categ = Category()
        categ.user_id = current_user.id
        categ.name = cat_name
        db_sess.add(categ)
        db_sess.commit()
    return redirect(url_for("show_goods"))


@app.route('/cat_del/<int:id_>', methods=['GET', 'POST'])
@login_required
def cat_del(id_):
    db_sess = db_session.create_session()
    cat = db_sess.query(Category).filter(Category.id == id_).first()
    if cat:
        db_sess.delete(cat)
        db_sess.commit()
    return redirect(url_for("show_goods"))


@app.route('/oplata/<int:all_total>', methods=['GET', 'POST'])
@login_required
def oplata(all_total):
    db_sess = db_session.create_session()
    cat = db_sess.query(Goods, Cart).join(Cart).filter(current_user.id == Cart.user_id, Goods.id == Cart.goods_id).all()
    for i in cat:
        if i[0].in_stock - i[1].amount >= 0 and i[1].amount > 0:
            i[0].in_stock = i[0].in_stock - i[1].amount
            db_sess.delete(i[1])
    db_sess.commit()

    # if cat:
    #     db_sess.delete(cat)
    #     db_sess.commit()
    #     db_sess.commit()
    return redirect(url_for("basket"))


def main():
    db_session.global_init("db/shop.sqlite3")
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
