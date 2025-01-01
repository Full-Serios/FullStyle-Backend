from models.worker_model import WorkerModel
from flask_restful import Resource

class Worker(Resource):
    # @jwt_required()
    def get(self):
        workers = WorkerModel.get_all_workers()

        if workers:
            workers_json = [worker.json() for worker in workers]
            return workers_json, 200
        return {"message": "Worker not found"}, 404