# import datetime
# import sqlalchemy
# from flask_login import UserMixin
# from sqlalchemy import orm
# from sqlalchemy_serializer import SerializerMixin
#
# from .db_session import SqlAlchemyBase
#
#
# class Comment(SqlAlchemyBase, UserMixin, SerializerMixin):
#     __tablename__ = 'comments'
#
#     id = sqlalchemy.Column(sqlalchemy.Integer,
#                            primary_key=True, autoincrement=True)
#     author_id = sqlalchemy.Column(sqlalchemy.Integer,
#                                   sqlalchemy.ForeignKey('users.id'))
#     goods_id = sqlalchemy.Column(sqlalchemy.Integer,
#                                   sqlalchemy.ForeignKey('goods.id'))
#     text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
#     created_date = sqlalchemy.Column(sqlalchemy.DateTime,
#                                   default=datetime.datetime.strptime(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "%d/%m/%Y %H:%M:%S"))  # дата написания
#
#     goods = orm.relationship('Goods')
#     user = orm.relationship('User')