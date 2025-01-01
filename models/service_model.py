from config.server_config import db

class ServiceModel(db.Model):
    # Para manejar tablas usando ORM
    __tablename__ = 'service'

    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100), nullable=False)
    description = db.Column("description", db.String, nullable=True)
    price = db.Column("price", db.Float, nullable=False)
    duration = db.Column("duration", db.Integer, nullable=False)

    # Constructor y funciones asociadas con la clase
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
    #   query = text("SELECT * FROM SERVICIO")
    #   services = db.session.execute(query).all()
    #   services_json = [{'id': service[0], 'nombre': service[1], 'descripcion': service[2], 'precio': service[3], 'duracion': service[4]} for service in services]
    #   return services_json
