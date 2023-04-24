import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Goods(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'goods'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    old_price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    discount = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    in_stock = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')

    categories = orm.relationship("Category",
                                  secondary="association",
                                  backref="goods")
