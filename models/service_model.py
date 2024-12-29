from config.server_config import db

class ServiceModel(db.Model):
    # To handle tables using ORM
    __tablename__ = 'service'

    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100), nullable=False)
    description = db.Column("description", db.String, nullable=True)
    price = db.Column("price", db.Float, nullable=False)
    duration = db.Column("duration", db.Integer, nullable=False)

    # Constructor and associated functions with the class
    def __init__(self, id, name, description, price, duration) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.duration = duration

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'duration': self.duration
        }
    
    @classmethod
    def get_all_services(cls):
        services = cls.query.all()
        return services
    
    # def get_all_services():
    #   query = text("SELECT * FROM SERVICE")
    #   services = db.session.execute(query).all()
    #   services_json = [{'id': service[0], 'name': service[1], 'description': service[2], 'price': service[3], 'duration': service[4]} for service in services]
    #   return services_json
