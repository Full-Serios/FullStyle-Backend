from config.server_config import db

class ServiceModel(db.Model):
    __tablename__ = 'service'

    id = db.Column("id", db.Integer, primary_key=True)
    category_id = db.Column("category_id", db.Integer, db.ForeignKey('category.id'), nullable=False)
    name = db.Column("name", db.String(100), nullable=False)

    def __init__(self, category_id, name, active=True) -> None:
        self.category_id = category_id
        self.name = name

    def json(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'name': self.name
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