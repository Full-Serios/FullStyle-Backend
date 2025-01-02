from config.server_config import db

class CategoryModel(db.Model):
    __tablename__ = 'category'

    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100), nullable=False, unique=True)

    def __init__(self, name) -> None:
        self.name = name

    def json(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_all_categories(cls):
        return cls.query.all()