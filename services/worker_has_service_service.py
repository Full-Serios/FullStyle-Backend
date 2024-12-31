from models.worker_has_service_model import WorkerHasServiceModel
from models.site_has_service_model import SiteHasServiceModel
from models.worker_model import WorkerModel
from flask_restful import Resource, reqparse

class WorkerHasService(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('worker_id', type=int, required=True, help="This field cannot be left blank!")
    parser.add_argument('service_id', type=int, required=True, help="This field cannot be left blank!")

    # @jwt_required()
    def get(self):
        worker_services = WorkerHasServiceModel.get_all_worker_services()

        if worker_services:
            worker_services_json = [worker_service.json() for worker_service in worker_services]
            return worker_services_json, 200
        return {"message": "Worker-Has-Service not found"}, 404

    # @jwt_required()
    def post(self):
        data = WorkerHasService.parser.parse_args()

        # Get the worker's site_id and site_manager_id
        worker = WorkerModel.query.filter_by(id=data['worker_id']).first()
        if not worker:
            return {"message": "Worker not found"}, 404

        # Check if the service_id is allowed for the worker's site
        site_service = SiteHasServiceModel.query.filter_by(site_id=worker.site_id, site_manager_id=worker.site_manager_id, service_id=data['service_id']).first()
        if not site_service:
            return {"message": "Service not allowed for this worker's site"}, 400

        worker_service = WorkerHasServiceModel(data['worker_id'], data['service_id'])
        try:
            worker_service.save_to_db()
        except:
            return {"message": "An error occurred inserting the worker-service relationship."}, 500

        return worker_service.json(), 201