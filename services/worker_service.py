from models.worker_model import WorkerModel
from models.worker_has_service_model import WorkerHasServiceModel
from models.availability_model import AvailabilityModel
from models.days_off_model import DaysOffModel
from models.seasonal_schedule_model import SeasonalScheduleModel
from flask_restful import Resource, reqparse, request
from datetime import datetime

class Worker(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=int, required=False)
    parser.add_argument('name', type=str, required=False)
    parser.add_argument('site_id', type=int, required=False)
    parser.add_argument('profilepicture', type=str, required=False)
    parser.add_argument('description', type=str, required=False)

    # @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args', required=False)
        parser.add_argument('name', type=str, location='args', required=False)
        parser.add_argument('site_id', type=int, location='args', required=False)
        parser.add_argument('service_id', type=int, location='args', required=False)
        args = parser.parse_args()

        query = WorkerModel.query.filter_by(active=True)

        if args['id']:
            query = query.filter_by(id=args['id'])

        if args['name']:
            query = query.filter(WorkerModel.name.ilike(f"%{args['name']}%"))

        if args['site_id']:
            query = query.filter_by(site_id=args['site_id'])

        if args['service_id']:
            worker_ids = [whs.worker_id for whs in WorkerHasServiceModel.query.filter_by(service_id=args['service_id']).all()]
            query = query.filter(WorkerModel.id.in_(worker_ids))

        workers = query.all()
        if workers:
            workers_json = [worker.json() for worker in workers]
            return workers_json, 200
        return {"message": "Worker not found"}, 404

    # @jwt_required()
    def post(self):
        data = Worker.parser.parse_args()
        worker = WorkerModel(
            name=data['name'],
            site_id=data['site_id'],
            profilepicture=data['profilepicture'],
            description=data['description']
        )
        try:
            worker.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred inserting the worker: {str(e)}"}, 500

        return worker.json(), 201

    # @jwt_required()
    def put(self):
        data = Worker.parser.parse_args()
        worker_id = data['id']

        if not worker_id:
            return {"message": "Worker ID is required"}, 400

        worker = WorkerModel.query.filter_by(id=worker_id).first()

        if worker:
            worker.name = data['name']
            worker.site_id = data['site_id']
            worker.profilepicture = data['profilepicture']
            worker.description = data['description']
        else:
            return {"message": "Worker not found"}, 404

        try:
            worker.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred updating the worker: {str(e)}"}, 500

        return worker.json(), 200

    # @jwt_required()
    def delete(self):
        worker_id = request.args.get('id')

        if not worker_id:
            return {"message": "Worker ID is required as a query parameter"}, 400

        worker = WorkerModel.query.filter_by(id=worker_id).first()

        if worker:
            try:
                worker.deactivate()
            except Exception as e:
                return {"message": f"An error occurred deactivating the worker: {str(e)}"}, 500
            return {"message": "Worker deactivated"}, 200
        return {"message": "Worker not found"}, 404

class WorkerAvailability(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('worker_id', type=int, location='args', required=True, help="This field cannot be left blank!")
    parser.add_argument('date', type=str, location='args', required=True, help="This field cannot be left blank!")
    parser.add_argument('time', type=str, location='args', required=True, help="This field cannot be left blank!")

    # @jwt_required()
    def get(self):
        args = WorkerAvailability.parser.parse_args()
        worker_id = args['worker_id']
        date_str = args['date']
        time_str = args['time']

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            time = datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            return {"message": "Invalid date or time format. Use 'YYYY-MM-DD' for date and 'HH:MM' for time."}, 400

        # Check if the worker is active
        worker = WorkerModel.query.filter_by(id=worker_id, active=True).first()
        if not worker:
            return {"message": "Worker not found or inactive"}, 404

        # Check if the worker has a day off
        dayoff = DaysOffModel.query.filter_by(worker_id=worker_id, dayoff=date).first()
        if dayoff:
            return {"message": "Worker is not available on this day"}, 200

        # Check if the worker has a seasonal schedule
        seasonal_schedule = SeasonalScheduleModel.query.filter(
            SeasonalScheduleModel.worker_id == worker_id,
            SeasonalScheduleModel.startdate <= date,
            SeasonalScheduleModel.enddate >= date
        ).first()
        if seasonal_schedule:
            if seasonal_schedule.starttime <= time <= seasonal_schedule.endtime:
                return {"message": "Worker is available"}, 200
            else:
                return {"message": "Worker is not available at this time"}, 200

        # Check the worker's regular availability
        weekday = date.strftime('%A')
        availability = AvailabilityModel.query.filter_by(worker_id=worker_id, weekday=weekday).all()
        for slot in availability:
            if slot.starttime <= time <= slot.endtime:
                return {"message": "Worker is available"}, 200

        return {"message": "Worker is not available at this time"}, 200