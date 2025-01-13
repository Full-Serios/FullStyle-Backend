from config.server_config import db

class DetailModel(db.Model):
    __tablename__ = 'detail'

    site_id = db.Column("site_id", db.Integer, db.ForeignKey('site.id', ondelete='CASCADE'), primary_key=True)
    service_id = db.Column("service_id", db.Integer, db.ForeignKey('service.id', ondelete='CASCADE'), primary_key=True)
    description = db.Column("description", db.Text, nullable=True)
    price = db.Column("price", db.Integer, nullable=False)
    duration = db.Column("duration", db.Integer, nullable=False)
    active = db.Column("active", db.Boolean, default=True, nullable=False)

    site = db.relationship('SiteModel', back_populates='details')
    service = db.relationship('ServiceModel', back_populates='details')

    def __init__(self, site_id, service_id, description, price, duration, active=True) -> None:
        self.site_id = site_id
        self.service_id = service_id
        self.description = description
        self.price = price
        self.duration = duration
        self.active = active

    def json(self):
        return {
            'site_id': self.site_id,
            'service_id': self.service_id,
            'description': self.description,
            'price': self.price,
            'duration': self.duration,
            'active': self.active
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def deactivate(self):
        self.active = False
        db.session.commit()

    @classmethod
    def get_all_details(cls):
        return cls.query.filter_by(active=True).all()

    @classmethod
    def find_by_site_and_service(cls, site_id, service_id):
        return cls.query.filter_by(site_id=site_id, service_id=service_id, active=True).first()