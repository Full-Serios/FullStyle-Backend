import re
import datetime
from config.server_config import db
from werkzeug.security import check_password_hash
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
    active = db.Column("active", db.Boolean, nullable=False, default=True)
    # otp_secret = db.Column("otp_secret", db.String(16), nullable=False)

    # Methods
    def __init__(self, email, name, password):
        self.email = email
        self.name = name
        self.password = password
        # self.otp_secret = b32encode(urandom(10)).decode("utf-8")

    def json(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "password": self.password,
            "active": self.active
        }
         
    @classmethod
    def get_all_users(cls):
        users = cls.query.all()
        return users
    
    # def get_totp_uri(self):
    #     return f"otpauth://totp/{self.email}?secret={self.otp_secret}&issuer=Flask"
    
    # def verify_totp(self, token):
    #     return valid_totp(token, self.otp_secret)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        self.is_active = False
        db.session.add(self)
        db.session.commit()

    def recover_user(self):
        self.is_active = True
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id, active=True).first()

    @staticmethod
    def is_valid_email(email):
        regex = re.compile(
            r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        )
        return re.fullmatch(regex, email)