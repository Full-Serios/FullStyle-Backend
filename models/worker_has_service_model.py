from config.server_config import db

class WorkerHasServiceModel(db.Model):
    # To handle tables using ORM
    __tablename__ = 'worker_has_service'

    worker_id = db.Column("worker_id", db.Integer, db.ForeignKey('worker.id'), primary_key=True)
    service_id = db.Column("service_id", db.Integer, db.ForeignKey('service.id'), primary_key=True)

    # Constructor and associated functions with the class
    def __init__(self, worker_id, service_id) -> None:
        self.worker_id = worker_id
        self.service_id = service_id

    def json(self):
        return {
            'worker_id': self.worker_id,
            'service_id': self.service_id
        }
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def get_all_worker_services(cls):
        worker_services = cls.query.all()
        return worker_services