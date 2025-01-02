from config.server_config import db

class SiteHasCategoryModel(db.Model):
    __tablename__ = 'site_has_category'

    site_id = db.Column("site_id", db.Integer, db.ForeignKey('site.id'), primary_key=True)
    category_id = db.Column("category_id", db.Integer, db.ForeignKey('category.id'), primary_key=True)

    def __init__(self, site_id, category_id) -> None:
        self.site_id = site_id
        self.category_id = category_id

    def json(self):
        return {
            'site_id': self.site_id,
            'category_id': self.category_id
        }
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def get_all_site_categories(cls):
        site_categories = cls.query.all()
        return site_categories