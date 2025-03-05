from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from datetime import timedelta
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from config.db_config import db
from config.routes_config import start_routes
import logging
from logging.handlers import RotatingFileHandler
import os

# Import models
from config.models_config import *

load_dotenv()

# Flask Environment Variables
SERVER_HOST = os.environ["HOST"]
SERVER_PORT = os.environ["PORT"]
SERVER_ENV = os.environ["ENV"]
SECRET_KEY = os.environ["SECRET_KEY"]
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
DATABASE_CONNECTION_URI = os.environ["DATABASE_URL"]
ENCRYPTION_KEY = os.environ["JWT_SECRET_KEY"]

def create_app():
    # Configuring the Flask app
    app = Flask(__name__)
    cors = CORS(app)

    logging.basicConfig(
        filename="logs/app.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Desactivar logs de Werkzeug (servidor de desarrollo)
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    app.secret_key = SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONNECTION_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

    # Configuring the Flask-JWT-Extended extension
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=15)

    # Configuración de Wompi
    # app.config["WOMPI_PUBLIC_KEY"] = os.environ["WOMPI_PUBLIC_KEY"]
    # app.config["WOMPI_PRIVATE_KEY"] = os.environ["WOMPI_PRIVATE_KEY"]
    # app.config["WOMPI_URL"] = os.environ["WOMPI_URL"]

    # Start the Flask-JWT-Extended and the Flask-ReSTful extension
    jwt = JWTManager(app)
    api = Api(app)

    with app.app_context():
        db.init_app(app)
        db.create_all()

    # @jwt.token_in_blocklist_loader
    # def check_if_token_is_revoked(jwt_header, jwt_payload):
    #     jti = jwt_payload["jti"]
    #     return TokenBlockListModel.is_token_blocked(jti)

    # Start the routes
    start_routes(api)

    return app

def run_server():
    app = create_app()
    is_dev_env = False if SERVER_ENV == "production" else True
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=is_dev_env)