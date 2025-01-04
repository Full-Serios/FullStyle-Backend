from config.server_config import db

class AppointmentModel(db.Model):
    __tablename__ = 'appointment'

    id = db.Column("id", db.Integer, primary_key=True)
    appointmenttime = db.Column("appointmenttime", db.DateTime, nullable=False)
    status = db.Column("status", db.String(50), default='pending', nullable=False)
    worker_id = db.Column("worker_id", db.Integer, db.ForeignKey('worker.id'), nullable=False)
    site_id = db.Column("site_id", db.Integer, nullable=False)
    service_id = db.Column("service_id", db.Integer, nullable=False)
    client_id = db.Column("client_id", db.Integer, nullable=False) # db.ForeignKey('client.id'), 

    def __init__(self, appointmenttime, status, worker_id, site_id, service_id, client_id) -> None:
        self.appointmenttime = appointmenttime
        self.status = status
        self.worker_id = worker_id
        self.site_id = site_id
        self.service_id = service_id
        self.client_id = client_id

    def json(self):
        return {
            'id': self.id,
            'appointmenttime': str(self.appointmenttime),
            'status': self.status,
            'worker_id': self.worker_id,
            'site_id': self.site_id,
            'service_id': self.service_id,
            'client_id': self.client_id
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_all_appointments(cls):
        return cls.query.all()

    @classmethod
    def find_by_id(cls, appointment_id):
        return cls.query.filter_by(id=appointment_id).first()