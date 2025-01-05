from models.worker_model import WorkerModel
from models.worker_has_service_model import WorkerHasServiceModel
from models.availability_model import AvailabilityModel
from models.days_off_model import DaysOffModel
from models.seasonal_schedule_model import SeasonalScheduleModel
from models.detail_model import DetailModel
from models.appointment_model import AppointmentModel
from flask_restful import Resource, reqparse, request
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
    
class WorkerWeeklySchedule(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('worker_id', type=int, location='args', required=True, help="This field cannot be left blank!")
    parser.add_argument('date', type=str, location='args', required=True, help="This field cannot be left blank!")

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

        # Initialize the schedule dictionary
        schedule = {day: {"available": [], "occupied": []} for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}

        # Get the worker's days off
        days_off = DaysOffModel.query.filter_by(worker_id=worker_id).filter(DaysOffModel.dayoff.between(week_start, week_end)).all()
        days_off_dates = [day_off.dayoff for day_off in days_off]

        # Get the worker's seasonal schedules
        seasonal_schedules = SeasonalScheduleModel.query.filter_by(worker_id=worker_id).filter(
            SeasonalScheduleModel.startdate <= week_end,
            SeasonalScheduleModel.enddate >= week_start
        ).all()

        # Get the worker's regular availability
        availability = AvailabilityModel.query.filter_by(worker_id=worker_id).all()

        # Get the worker's appointments
        appointments = AppointmentModel.query.filter_by(worker_id=worker_id).filter(
            AppointmentModel.appointmenttime.between(week_start, week_end)
        ).all()

        # Populate the schedule
        for i in range(7):
            current_date = week_start + timedelta(days=i)
            weekday = current_date.strftime('%A')

            if current_date in days_off_dates:
                continue

            # Check for seasonal schedule
            seasonal_schedule = next((s for s in seasonal_schedules if s.startdate <= current_date <= s.enddate), None)
            if seasonal_schedule:
                schedule[weekday]["available"].append({"start": str(seasonal_schedule.starttime), "end": str(seasonal_schedule.endtime)})
            else:
                # Regular availability
                for slot in availability:
                    if slot.weekday == weekday:
                        schedule[weekday]["available"].append({"start": str(slot.starttime), "end": str(slot.endtime)})

            # Occupied times (appointments)
            for appointment in appointments:
                if appointment.appointmenttime.date() == current_date:
                    end_time = (appointment.appointmenttime + timedelta(minutes=DetailModel.query.filter_by(site_id=worker.site_id, service_id=appointment.service_id).first().duration)).time()
                    schedule[weekday]["occupied"].append({"start": str(appointment.appointmenttime.time()), "end": str(end_time)})

        return {
            "worker_id": worker_id,
            "week_start": str(week_start),
            "week_end": str(week_end),
            "schedule": schedule
        }, 200