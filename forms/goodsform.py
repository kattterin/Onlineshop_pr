from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField, FloatField, FileField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class GoodForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    slug = StringField('Слог', validators=[DataRequired()])

    content = TextAreaField("Содержание")
    # is_private = BooleanField("Личное")
    category = SelectMultipleField("Категории", coerce=int, validators=[DataRequired()])
    brand = SelectField("Бренд", coerce=int)
    price = FloatField("Цена")
    old_price = FloatField("Старая цена")
    submit = SubmitField('Применить')
