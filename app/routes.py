from flask import Blueprint, render_template, jsonify
import pandas as pd
from sqlalchemy import create_engine, text
import json
from decimal import Decimal
from dotenv import load_dotenv
import os

main = Blueprint('main', __name__)

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la URL de conexión desde las variables de entorno
URL = os.getenv('DATABASE_URL')
engine = create_engine(URL)

@main.route("/")
def home():
    query = text("SELECT * FROM SERVICIO")
    
    # Leer la tabla SQL como un dataframe
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    
    # Ejecutar como una consulta SQL nativa
    with engine.connect() as connection:
        result = connection.execute(query)
        rows = result.fetchall()
        column_names = result.keys()

        data = []
        for row in rows:
            row_dict = {}
            for i, column_name in enumerate(column_names):
                if isinstance(row[i], Decimal): # Convertir tipo Decimal a float
                    row_dict[column_name] = float(row[i])
                else:
                    row_dict[column_name] = row[i]
            data.append(row_dict)

    json_data = json.dumps(data, indent=4)
    
    return render_template("home.html", json_data=json_data, dataframe=df.to_html())

@main.route("/about")
def about():
    return render_template("about.html")