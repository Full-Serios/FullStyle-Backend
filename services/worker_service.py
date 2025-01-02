from models.worker_model import WorkerModel
from flask_restful import Resource, reqparse

class Worker(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=int, required=False)
    parser.add_argument('name', type=str, required=True, help="This field cannot be left blank!")
    parser.add_argument('availability', type=dict, required=False)
    parser.add_argument('busy', type=bool, required=False)
    parser.add_argument('site_id', type=int, required=True, help="This field cannot be left blank!")
    parser.add_argument('site_manager_id', type=int, required=True, help="This field cannot be left blank!")

    # @jwt_required()
    def get(self):
        workers = WorkerModel.get_all_workers()

        if workers:
            workers_json = [worker.json() for worker in workers]
            return workers_json, 200
        return {"message": "Worker not found"}, 404

    # @jwt_required()
    def post(self):
        data = Worker.parser.parse_args()
        worker = WorkerModel(data['id'], data['name'], data['availability'], data['busy'], data['site_id'], data['site_manager_id'])
        try:
            worker.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred inserting the worker: {str(e)}"}, 500

        return worker.json(), 201