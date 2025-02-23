from config.server_config import db

class ClientModel(db.Model):
    __tablename__ = 'client'

    id = db.Column("id", db.Integer, primary_key=True)

    def __init__(self, id) -> None:
        self.id = id

    def json(self):
        return {
            'id': self.id
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_all_clients(cls):
        return cls.query.all()

    @classmethod
    def find_by_id(cls, client_id):
        return cls.query.filter_by(id=client_id).first()