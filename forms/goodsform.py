from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField, FloatField, FileField
from wtforms import BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed


class GoodForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    # is_private = BooleanField("Личное")
    category = SelectMultipleField("Категории", coerce=int, validators=[DataRequired()])
    price = IntegerField("Цена")
    in_stock = IntegerField('Количество товара')
    old_price = IntegerField("Старая цена")
    submit = SubmitField('Применить')

