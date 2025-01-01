import re
import datetime
from config.server_config import db
from os import urandom 
from base64 import b32encode
from onetimepass import valid_totp
import utils.encryption as encryption


class UserModel(db.Model):
    __tablename__ = "userr"

    # Attributes
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100), nullable=False)
    email = db.Column("email", db.String(150), nullable=False, unique=True)
    password = db.Column("password", db.String(255), nullable=False)

    # is_active = db.Column("activo", db.Boolean, nullable=False, default=True)

    # Methods
    def __init__(self, email, name, password):
        self.email = email
        self.name = name
        self.password = password

    def json(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
        }
        
    @classmethod
    def get_all_users(cls):
        users = cls.query.all()
        return users