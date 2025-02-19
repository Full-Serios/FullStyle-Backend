from config.server_config import db

class NotificationModel(db.Model):
    __tablename__ = 'notification'

    id = db.Column("id", db.Integer, primary_key=True)
    timestamp = db.Column("timestamp", db.DateTime, server_default=db.func.current_timestamp())
    type = db.Column("type", db.String(50), nullable=False)
    status = db.Column("status", db.String(50), default='pending', nullable=False)
    appointment_id = db.Column("appointment_id", db.Integer, db.ForeignKey('appointment.id', ondelete='CASCADE'), nullable=False)

    appointment = db.relationship('AppointmentModel')

    def __init__(self, type, appointment_id, status='pending', timestamp=None) -> None:
        self.type = type
        self.status = status
        self.appointment_id = appointment_id
        if timestamp:
            self.timestamp = timestamp

    def json(self):
        return {
            'id': self.id,
            'timestamp': str(self.timestamp),
            'type': self.type,
            'status': self.status,
            'appointment_id': self.appointment_id
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_all_notifications(cls):
        return cls.query.all()

    @classmethod
    def find_by_id(cls, notification_id):
        return cls.query.filter_by(id=notification_id).first()