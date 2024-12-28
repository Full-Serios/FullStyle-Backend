from sqlalchemy import Column, Integer, String, Float
from src.database.db_connection import Base

class SERVICIO(Base):
    # Para manejar tablas usando ORM
    __tablename__ = 'SERVICIO'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    descripcion = Column(String)
    precio = Column(Float)
    duracion = Column(Integer)

    # Constructor y funciones asociadas con la clase
    def __init__(self, id, nombre, descripcion, precio, duracion) -> None:
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.duracion = duracion

    def to_json(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': self.precio,
            'duracion': self.duracion
        }