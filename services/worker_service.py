from models.worker_model import WorkerModel
from models.worker_has_service_model import WorkerHasServiceModel
from models.availability_model import AvailabilityModel
from models.days_off_model import DaysOffModel
from models.seasonal_schedule_model import SeasonalScheduleModel
from models.detail_model import DetailModel
from models.appointment_model import AppointmentModel
from flask_restful import Resource, reqparse, request
from utils.helpers import (
    check_worker_exists,
    check_worker_active,
    check_site_exists,
    compute_daily_schedule
)
from datetime import datetime, timedelta

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
        worker = WorkerModel.query.filter_by(id=data['id']).first()

        if worker:
            if not worker.active:
                worker.active = True
                worker.name = data['name']
                worker.site_id = data['site_id']
                worker.profilepicture = data['profilepicture']
                worker.description = data['description']
                try:
                    worker.save_to_db()
                except Exception as e:
                    return {"message": f"An error occurred updating the worker: {str(e)}"}, 500
                return worker.json(), 200
            else:
                return {"message": "Worker already exists and is active"}, 400
        else:
            # Check if site exists
            if data['site_id']:
                site, error = check_site_exists(data['site_id'])
                if error:
                    return {"message": error}, 400

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

        worker, error = check_worker_exists(worker_id)
        if error:
            return {"message": error}, 404

        # Check if site exists
        if data['site_id']:
            site, error = check_site_exists(data['site_id'])
            if error:
                return {"message": error}, 400

        worker.name = data['name']
        worker.site_id = data['site_id']
        worker.profilepicture = data['profilepicture']
        worker.description = data['description']

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

        worker, error = check_worker_exists(worker_id)
        if error:
            return {"message": error}, 404

        try:
            worker.deactivate()
        except Exception as e:
            return {"message": f"An error occurred deactivating the worker: {str(e)}"}, 500
        return {"message": "Worker deactivated"}, 200
    
class WorkerDailySchedule(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('worker_id', type=int, location='args', required=True, help="worker_id is required")
    parser.add_argument('date', type=str, location='args', required=True, help="date is required in 'YYYY-MM-DD' format")

    # @jwt_required()
    def get(self):
        args = WorkerDailySchedule.parser.parse_args()
        worker_id = args['worker_id']
        date_str = args['date']
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return {"message": "Invalid date format. Use 'YYYY-MM-DD'."}, 400

        # Check if the worker is active
        worker = WorkerModel.query.filter_by(id=worker_id, active=True).first()
        if not worker:
            return {"message": "Worker not found or inactive"}, 404

        schedule = compute_daily_schedule(worker, date)

        return {
            "worker_id": worker_id, 
            "date": str(date), 
            "schedule": schedule
        }, 200

class WorkerWeeklySchedule(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('worker_id', type=int, location='args', required=True, help="worker_id is required")
    parser.add_argument('date', type=str, location='args', required=True, help="date is required in 'YYYY-MM-DD' format")

    # @jwt_required()
    def get(self):
        args = WorkerWeeklySchedule.parser.parse_args()
        worker_id = args['worker_id']
        date_str = args['date']
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return {"message": "Invalid date format. Use 'YYYY-MM-DD'."}, 400

        # Calculate the start and end of the week
        week_start = date - timedelta(days=date.weekday())
        week_end = week_start + timedelta(days=6)

        # Check if the worker is active
        worker = WorkerModel.query.filter_by(id=worker_id, active=True).first()
        if not worker:
            return {"message": "Worker not found or inactive"}, 404

        # Calculate 7 days of schedule
        schedule = {}
        current_date = week_start
        for i in range(7):
            day_name = current_date.strftime('%A')
            daily_schedule = compute_daily_schedule(worker, current_date)
            schedule[day_name] = daily_schedule
            current_date += timedelta(days=1)

        return {
            "worker_id": worker_id,
            "week_start": str(week_start),
            "week_end": str(week_end),
            "schedule": schedule
        }, 200