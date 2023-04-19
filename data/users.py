import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import Column, JSON, orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class UsersPassword:
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f"""id:{self.id}, name:{self.name}, email:{self.email}"""


class User(SqlAlchemyBase, UsersPassword, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = Column(sqlalchemy.Integer,
                primary_key=True, autoincrement=True)
    name = Column(sqlalchemy.String, nullable=True)
    email = Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    phone = Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = Column(sqlalchemy.String, nullable=True)
    basket = Column(JSON)
