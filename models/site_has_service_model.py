from config.server_config import db

class SiteHasServiceModel(db.Model):
    # To handle tables using ORM
    __tablename__ = 'site_has_service'

    site_id = db.Column("site_id", db.Integer, db.ForeignKey('site.id'), primary_key=True)
    site_manager_id = db.Column("site_manager_id", db.Integer, primary_key=True)
    service_id = db.Column("service_id", db.Integer, db.ForeignKey('service.id'), primary_key=True)

    # Constructor and associated functions with the class
    def __init__(self, site_id, site_manager_id, service_id) -> None:
        self.site_id = site_id
        self.site_manager_id = site_manager_id
        self.service_id = service_id

    def json(self):
        return {
            'site_id': self.site_id,
            'site_manager_id': self.site_manager_id,
            'service_id': self.service_id
        }
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def get_all_site_services(cls):
        site_services = cls.query.all()
        return site_services