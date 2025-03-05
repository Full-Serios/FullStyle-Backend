from flask import Flask, jsonify
from flask_restful import Api, Resource
import os
from flask_jwt_extended import jwt_required

LOG_FILE_PATH = "logs/app.log"  # Ruta del archivo de logs

class GetLogs(Resource):
    # @jwt_required()
    def get(self):
        if not os.path.exists(LOG_FILE_PATH):
            return {"error": "Log file not found"}, 404

        try:
            with open(LOG_FILE_PATH, "r") as log_file:
                logs = log_file.readlines()  # Leer todas las líneas del log

            return {"logs": logs}, 200
        except Exception as e:
            return {"error": f"Could not read log file: {str(e)}"}, 500
