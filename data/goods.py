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
    slug = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.LargeBinary, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.REAL, nullable=True)
    old_price = sqlalchemy.Column(sqlalchemy.REAL, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')

    categories = orm.relationship("Category",
                                  secondary="association",
                                  backref="goods")
    brandies = orm.relationship("Brand",
                                secondary="association2",
                                backref="goods")
