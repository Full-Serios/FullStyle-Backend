from models.service_model import ServiceModel
from datetime import datetime, timezone
from flask_restful import Resource, reqparse
from flask_jwt_extended import get_jwt_identity, jwt_required

class Service(Resource):
    # @jwt_required()
    def get(self):
        services = ServiceModel.get_all_services()

        if services:
            services_json = [service.json() for service in services]
            return services_json, 200
        return {"message": "User not found"}, 404