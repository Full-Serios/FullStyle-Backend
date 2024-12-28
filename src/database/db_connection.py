from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la URL de conexión desde las variables de entorno
DATABASE_URL = os.getenv('DATABASE_URL')

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL)

# Crear una base declarativa
Base = declarative_base()

# Crear una fábrica de sesiones
Session = sessionmaker(bind=engine)