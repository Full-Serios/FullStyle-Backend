from config.server_config import db

class SiteModel(db.Model):
    # To handle tables using ORM
    __tablename__ = 'site'

    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(150), nullable=False)
    address = db.Column("address", db.String(255), nullable=False)
    phone = db.Column("phone", db.String(20), nullable=True)
    manager_id = db.Column("manager_id", db.Integer, nullable=False) # db.ForeignKey('manager.id', ondelete='CASCADE'), 
    photos = db.Column("photos", db.JSON, nullable=True)

    details = db.relationship('DetailModel', back_populates='site', cascade="all, delete-orphan")
    workers = db.relationship('WorkerModel', back_populates='site', cascade="all, delete-orphan")
    site_categories = db.relationship('SiteHasCategoryModel', back_populates='site', cascade="all, delete-orphan")

    # Constructor and associated functions with the class
    def __init__(self, id, name, address, phone, manager_id, photos) -> None:
        self.id = id
        self.name = name
        self.address = address
        self.phone = phone
        self.manager_id = manager_id
        self.photos = photos

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'manager_id': self.manager_id,
            'photos': self.photos
        }
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def get_all_sites(cls):
        sites = cls.query.all()
        return sites