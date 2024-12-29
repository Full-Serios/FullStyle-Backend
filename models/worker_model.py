from config.server_config import db

class WorkerModel(db.Model):
    # To handle tables using ORM
    __tablename__ = 'worker'

    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100), nullable=False)
    availability = db.Column("availability", db.JSON, nullable=True)
    busy = db.Column("busy", db.Boolean, nullable=True)
    site_id = db.Column("site_id", db.Integer, nullable=False)
    site_manager_id = db.Column("site_manager_id", db.Integer, nullable=False)

    # Constructor and associated functions with the class
    def __init__(self, id, name, availability, busy, site_id, site_manager_id) -> None:
        self.id = id
        self.name = name
        self.availability = availability
        self.busy = busy
        self.site_id = site_id
        self.site_manager_id = site_manager_id

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'availability': self.availability,
            'busy': self.busy,
            'site_id': self.site_id,
            'site_manager_id': self.site_manager_id
        }
    
    @classmethod
    def get_all_workers(cls):
        workers = cls.query.all()
        return workers