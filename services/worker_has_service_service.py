from models.worker_has_service_model import WorkerHasServiceModel
from flask_restful import Resource

class WorkerHasService(Resource):
    # @jwt_required()
    def get(self):
        worker_services = WorkerHasServiceModel.get_all_worker_services()

        if worker_services:
            worker_services_json = [worker_service.json() for worker_service in worker_services]
            return worker_services_json, 200
        return {"message": "Worker-Has-Service not found"}, 404