from config.server_config import db
from models.category_model import CategoryModel

class ServiceModel(db.Model):
    __tablename__ = 'service'

    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100), nullable=False)
    description = db.Column("description", db.String, nullable=True)
    price = db.Column("price", db.Float, nullable=False)
    duration = db.Column("duration", db.Integer, nullable=False)
    category_id = db.Column("category_id", db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __init__(self, id, name, description, price, duration, category_id) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.duration = duration
        self.category_id = category_id

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'duration': self.duration,
            'category_id': self.category_id
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_all_services(cls):
        return cls.query.all()

    @classmethod
    def find_by_id(cls, service_id):
        return cls.query.filter_by(id=service_id).first()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_category(cls, category_id):
        return cls.query.filter_by(category_id=category_id).all()

    @classmethod
    def delete_by_id(cls, service_id):
        service = cls.find_by_id(service_id)
        if service:
            db.session.delete(service)
            db.session.commit()