from config.server_config import db

class WorkerModel(db.Model):
    __tablename__ = 'worker'

    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100), nullable=False)
    site_id = db.Column("site_id", db.Integer, db.ForeignKey('site.id', ondelete='CASCADE'), nullable=False)
    profilepicture = db.Column("profilepicture", db.String(255), nullable=True)
    description = db.Column("description", db.Text, nullable=True)
    active = db.Column("active", db.Boolean, default=True, nullable=False)

    site = db.relationship('SiteModel', back_populates='workers')
    availabilities = db.relationship('AvailabilityModel', back_populates='worker', cascade="all, delete-orphan")
    days_off = db.relationship('DaysOffModel', back_populates='worker', cascade="all, delete-orphan")
    seasonal_schedules = db.relationship('SeasonalScheduleModel', back_populates='worker', cascade="all, delete-orphan")
    worker_services = db.relationship('WorkerHasServiceModel', back_populates='worker', cascade="all, delete-orphan")
    appointments = db.relationship('AppointmentModel', back_populates='worker', cascade="all, delete-orphan")

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