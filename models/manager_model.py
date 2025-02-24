from config.server_config import db
from sqlalchemy.orm import relationship

class ManagerModel(db.Model):
    __tablename__ = "manager"
    
    # Attributes
    id = db.Column("id", db.Integer, db.ForeignKey('userr.id'), primary_key=True)
    bankaccount = db.Column("bankaccount", db.BigInteger, nullable=False)
    accounttype = db.Column("accounttype", db.String(45), nullable=False)
    bankentity = db.Column("bankentity", db.String(45), nullable=False)
    subscriptionactive = db.Column("subscriptionactive", db.Boolean, nullable=False, default=False)
    subscriptionstartdate = db.Column("subscriptionstartdate", db.DateTime(timezone=True))
    subscriptiontype = db.Column("subscriptiontype", db.String(45))
    subscriptionfinishdate = db.Column("subscriptionfinishdate", db.DateTime(timezone=True))
    
    # Relationship
    user = relationship("UserModel", back_populates="manager")
    
    def __init__(self, bankaccount, accounttype, bankentity, userModel, 
                 subscriptiontype=None, subscriptionstartdate=None, subscriptionfinishdate=None):
        self.id = userModel.id  # Asignar el ID del usuario
        self.bankaccount = bankaccount
        self.accounttype = accounttype
        self.bankentity = bankentity
        self.subscriptiontype = subscriptiontype
        self.subscriptionstartdate = subscriptionstartdate
        self.subscriptionfinishdate = subscriptionfinishdate

    def json(self):
        return {
            "id": self.id,
            "bankaccount": self.bankaccount,
            "accounttype": self.accounttype,
            "bankentity": self.bankentity,
            "subscriptionactive": self.subscriptionactive,
            "subscriptionstartdate": str(self.subscriptionstartdate) if self.subscriptionstartdate else None,
            "subscriptiontype": self.subscriptiontype,
            "subscriptionfinishdate": str(self.subscriptionfinishdate) if self.subscriptionfinishdate else None
        }
         
    @classmethod
    def get_all_managers(cls):
        managers = cls.query.all()
        return managers
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()