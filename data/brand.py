import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase

association_table = sqlalchemy.Table(
    'association2',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('goods', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('goods.id')),
    sqlalchemy.Column('brand', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('brand.id'))
)


class Brand(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'brand'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
