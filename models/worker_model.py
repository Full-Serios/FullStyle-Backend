from config.server_config import db

class WorkerModel(db.Model):
    __tablename__ = 'worker'

    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100), nullable=False)
    site_id = db.Column("site_id", db.Integer, db.ForeignKey('site.id'), nullable=False)
    profilepicture = db.Column("profilepicture", db.String(255), nullable=True)
    description = db.Column("description", db.Text, nullable=True)
    active = db.Column("active", db.Boolean, default=True, nullable=False)

    def __init__(self, name, site_id, profilepicture=None, description=None, active=True) -> None:
        self.name = name
        self.site_id = site_id
        self.profilepicture = profilepicture
        self.description = description
        self.active = active

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'site_id': self.site_id,
            'profilepicture': self.profilepicture,
            'description': self.description,
            'active': self.active
        }
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def deactivate(self):
        self.active = False
        db.session.commit()
    
    @classmethod
    def get_all_workers(cls):
        workers = cls.query.filter_by(active=True).all()
        return workers