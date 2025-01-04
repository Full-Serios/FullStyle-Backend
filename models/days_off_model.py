from config.server_config import db

class DaysOffModel(db.Model):
    __tablename__ = 'days_off'

    id = db.Column("id", db.Integer, primary_key=True)
    worker_id = db.Column("worker_id", db.Integer, db.ForeignKey('worker.id'), nullable=False)
    dayoff = db.Column("dayoff", db.Date, nullable=False)

    def __init__(self, worker_id, dayoff) -> None:
        self.worker_id = worker_id
        self.dayoff = dayoff

    def json(self):
        return {
            'id': self.id,
            'worker_id': self.worker_id,
            'dayoff': str(self.dayoff)
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_all_days_off(cls):
        return cls.query.all()