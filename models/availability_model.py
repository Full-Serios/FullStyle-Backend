from config.server_config import db

class AvailabilityModel(db.Model):
    __tablename__ = 'availability'

    id = db.Column("id", db.Integer, primary_key=True)
    worker_id = db.Column("worker_id", db.Integer, db.ForeignKey('worker.id', ondelete='CASCADE'), nullable=False)
    weekday = db.Column("weekday", db.String(10), nullable=False)
    starttime = db.Column("starttime", db.Time, nullable=False)
    endtime = db.Column("endtime", db.Time, nullable=False)

    worker = db.relationship('WorkerModel', back_populates='availabilities')

    def __init__(self, worker_id, weekday, starttime, endtime) -> None:
        self.worker_id = worker_id
        self.weekday = weekday
        self.starttime = starttime
        self.endtime = endtime

    def json(self):
        return {
            'id': self.id,
            'worker_id': self.worker_id,
            'weekday': self.weekday,
            'starttime': str(self.starttime),
            'endtime': str(self.endtime)
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_all_availabilities(cls):
        return cls.query.all()