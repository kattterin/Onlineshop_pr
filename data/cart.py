import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Cart(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'cart'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey('users.id'))
    goods_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey('goods.id'))
    amount = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    total = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)


    goods = orm.relationship('Goods')
    user = orm.relationship('User')