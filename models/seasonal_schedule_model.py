from config.server_config import db

class SeasonalScheduleModel(db.Model):
    __tablename__ = 'seasonal_schedule'

    id = db.Column("id", db.Integer, primary_key=True)
    worker_id = db.Column("worker_id", db.Integer, db.ForeignKey('worker.id'), nullable=False)
    seasonname = db.Column("seasonname", db.String(50), nullable=False)
    startdate = db.Column("startdate", db.Date, nullable=False)
    enddate = db.Column("enddate", db.Date, nullable=False)
    starttime = db.Column("starttime", db.Time, nullable=False)
    endtime = db.Column("endtime", db.Time, nullable=False)

    def __init__(self, worker_id, seasonname, startdate, enddate, starttime, endtime) -> None:
        self.worker_id = worker_id
        self.seasonname = seasonname
        self.startdate = startdate
        self.enddate = enddate
        self.starttime = starttime
        self.endtime = endtime

    def json(self):
        return {
            'id': self.id,
            'worker_id': self.worker_id,
            'seasonname': self.seasonname,
            'startdate': str(self.startdate),
            'enddate': str(self.enddate),
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
    def get_all_seasonal_schedules(cls):
        return cls.query.all()