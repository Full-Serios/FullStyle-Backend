from sqlalchemy import text
from src.database.db_connection import engine

def get_all_services():
    query = text("SELECT * FROM SERVICIO")
    with engine.connect() as connection:
        result = connection.execute(query)
        servicios = result.fetchall()
    return servicios

def add_service(nombre, descripcion, precio, duracion):
    query = text(f"""
        INSERT INTO SERVICIO (nombre, descripcion, precio, duracion)
        VALUES ({nombre}, {descripcion}, {precio}, {duracion})
    """)
    with engine.connect() as connection:
        connection.execute(query)