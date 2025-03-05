import re
import datetime
from config.server_config import db
from werkzeug.security import check_password_hash
from os import urandom
from base64 import b32encode
from onetimepass import valid_totp
import utils.encryption as encryption
from sqlalchemy.orm import relationship

class UserModel(db.Model):
    __tablename__ = "userr"

    # Attributes
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100), nullable=False)
    email = db.Column("email", db.String(150), nullable=False, unique=True)
    password = db.Column("password", db.String(255), nullable=True)
    active = db.Column("active", db.Boolean, nullable=False, default=True)
    auth_provider = db.Column("auth_provider", db.String(20), nullable=False, default='credentials')
    google_id = db.Column("google_id", db.String(100), unique=True, nullable=True)
    otp_secret = db.Column("otp_secret", db.String(16), nullable=True)  # Secreto OTP opcional

    manager = relationship("ManagerModel", back_populates="user", uselist=False)

    # Constructor
    def __init__(self, email, name, password, auth_provider='credentials', google_id=None):
        self.email = email
        self.name = name
        self.password = password
        self.auth_provider = auth_provider
        self.google_id = google_id

    def json(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "active": self.active,
            "auth_provider": self.auth_provider,
            "google_id": self.google_id
        }

    def check_password(self, password):
        """Verifica la contraseña ingresada."""
        if self.auth_provider == 'google':
            return False
        return check_password_hash(self.password, password)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        self.active = False
        db.session.add(self)
        db.session.commit()

    def recover_user(self):
        self.active = True
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id, active=True).first()

    @classmethod
    def is_manager(cls, id):
        user = cls.query.filter_by(id=id, active=True).first()
        if user is None:
            return False
        return user.manager is not None

    @classmethod
    def find_by_google_id(cls, google_id):
        return cls.query.filter_by(google_id=google_id, active=True).first()

    @staticmethod
    def is_valid_email(email):
        regex = re.compile(
            r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        )
        return re.fullmatch(regex, email)
