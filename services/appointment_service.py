from models.appointment_model import AppointmentModel
from flask_restful import Resource, reqparse, request
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import func
from utils.helpers import (
    check_appointment_time,
    check_appointment_exists,
    is_worker_available
)

class Appointment(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=int, required=False)
    parser.add_argument('appointmenttime', type=str, required=True, help="This field cannot be left blank!")
    parser.add_argument('status', type=str, required=False, default='pending')
    parser.add_argument('worker_id', type=int, required=True, help="This field cannot be left blank!")
    parser.add_argument('site_id', type=int, required=True, help="This field cannot be left blank!")
    parser.add_argument('service_id', type=int, required=True, help="This field cannot be left blank!")
    parser.add_argument('client_id', type=int, required=True, help="This field cannot be left blank!")

    # @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args', required=False)
        parser.add_argument('status', type=str, location='args', required=False)
        parser.add_argument('worker_id', type=int, location='args', required=False)
        parser.add_argument('site_id', type=int, location='args', required=False)
        parser.add_argument('service_id', type=int, location='args', required=False)
        parser.add_argument('client_id', type=int, location='args', required=False)
        args = parser.parse_args()

        query = AppointmentModel.query

        if args['id']:
            query = query.filter_by(id=args['id'])

        if args['status']:
            query = query.filter_by(status=args['status'])

        if args['worker_id']:
            query = query.filter_by(worker_id=args['worker_id'])

        if args['site_id']:
            query = query.filter_by(site_id=args['site_id'])

        if args['service_id']:
            query = query.filter_by(service_id=args['service_id'])

        if args['client_id']:
            query = query.filter_by(client_id=args['client_id'])

        appointments = query.all()

        if appointments:
            appointments_json = [appointment.json() for appointment in appointments]
            return appointments_json, 200
        return {"message": "Appointment not found"}, 404

    # @jwt_required()
    def post(self):
        data = Appointment.parser.parse_args()
        appointmenttime, error = check_appointment_time(data['appointmenttime'])
        if error:
            return {"message": error}, 400

        available, message = is_worker_available(data['worker_id'], appointmenttime.date(), appointmenttime.time(), data['service_id'])
        if not available:
            return {"message": message}, 400

        appointment = AppointmentModel(
            appointmenttime=appointmenttime,
            status=data['status'],
            worker_id=data['worker_id'],
            site_id=data['site_id'],
            service_id=data['service_id'],
            client_id=data['client_id']
        )
        try:
            appointment.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred inserting the appointment: {str(e)}"}, 500

        return appointment.json(), 201

    # @jwt_required()
    def put(self):
        data = Appointment.parser.parse_args()
        appointment_id = data['id']

        if not appointment_id:
            return {"message": "Appointment ID is required"}, 400

        appointment = AppointmentModel.find_by_id(appointment_id)

        appointment, error = check_appointment_exists(appointment_id)
        if error:
            return {"message": error}, 404

        appointmenttime, error = check_appointment_time(data['appointmenttime'])
        if error:
            return {"message": error}, 400

        available, message = is_worker_available(data['worker_id'], appointmenttime.date(), appointmenttime.time(), data['service_id'], current_appointment_id=appointment_id)
        if not available:
            return {"message": message}, 400

        appointment.appointmenttime = appointmenttime
        appointment.status = data['status']
        appointment.worker_id = data['worker_id']
        appointment.site_id = data['site_id']
        appointment.service_id = data['service_id']
        appointment.client_id = data['client_id']

        try:
            appointment.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred updating the appointment: {str(e)}"}, 500

        return appointment.json(), 200

    # @jwt_required()
    def delete(self):
        appointment_id = request.args.get('id')

        if not appointment_id:
            return {"message": "Appointment ID is required as a query parameter"}, 400
        
        appointment, error = check_appointment_exists(appointment_id)
        if error:
            return {"message": error}, 404

        if appointment:
            try:
                appointment.delete_from_db()
            except Exception as e:
                return {"message": f"An error occurred deleting the appointment: {str(e)}"}, 500
            return {"message": "Appointment deleted"}, 200
        return {"message": "Appointment not found"}, 404

# How many appointments have been made with an specific worker in a site
class WorkerStatistics(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('site_id', type=int, required=True, location='args', help="site_id is required")
    parser.add_argument('period', type=str, required=False, default='total', location='args', help="Period can be total, daily, weekly, monthly")
    parser.add_argument('count_periods', type=int, required=False, default=0, location='args', help="Number of days/weeks/months to include from current date backwards if > 0")

    # @jwt_required()
    def get(self):
        args = WorkerStatistics.parser.parse_args()
        site_id = args['site_id']
        period = args['period'].lower()
        count_periods = args['count_periods']
        
        now = datetime.now()

        # Number of days/weeks/months to include from current date backwards
        if count_periods > 0:
            if period == 'daily':
                start_date = now - relativedelta(days=count_periods)
            elif period == 'weekly':
                start_date = now - relativedelta(weeks=count_periods)
            elif period == 'monthly':
                start_date = now - relativedelta(months=count_periods)
            else:
                start_date = None
        else:
            start_date = None
        
        base_query = AppointmentModel.query.filter(AppointmentModel.site_id == site_id)
        if start_date:
            base_query = base_query.filter(AppointmentModel.appointmenttime >= start_date, AppointmentModel.appointmenttime <= now)
        
        if period == 'total':
            results = (
                base_query
                .with_entities(AppointmentModel.worker_id, func.count(AppointmentModel.id).label("total"))
                .group_by(AppointmentModel.worker_id)
                .all()
            )
        elif period == 'monthly':
            results = (
                base_query
                .with_entities(
                    AppointmentModel.worker_id,
                    func.extract('year', AppointmentModel.appointmenttime).label("year"),
                    func.extract('month', AppointmentModel.appointmenttime).label("month"),
                    func.count(AppointmentModel.id).label("total")
                )
                .group_by(AppointmentModel.worker_id,
                          func.extract('year', AppointmentModel.appointmenttime),
                          func.extract('month', AppointmentModel.appointmenttime))
                .all()
            )
        elif period == 'weekly':
            results = (
                base_query
                .with_entities(
                    AppointmentModel.worker_id,
                    func.date_trunc('week', AppointmentModel.appointmenttime).label("week_start"),
                    func.count(AppointmentModel.id).label("total")
                )
                .group_by(AppointmentModel.worker_id, func.date_trunc('week', AppointmentModel.appointmenttime))
                .all()
            )
        elif period == 'daily':
            results = (
                base_query
                .with_entities(
                    AppointmentModel.worker_id,
                    func.date(AppointmentModel.appointmenttime).label("day"),
                    func.count(AppointmentModel.id).label("total")
                )
                .group_by(AppointmentModel.worker_id, func.date(AppointmentModel.appointmenttime))
                .all()
            )
        else:
            return {"message": "Invalid period parameter. Use total, daily, weekly or monthly"}, 400

        # Format results
        stats = []
        for item in results:
            record = {"worker_id": item.worker_id, "total": item.total}
            if period == 'daily':
                record["day"] = item.day.strftime('%Y-%m-%d')
            if period == 'weekly':
                record["week_start"] = item.week_start.strftime('%Y-%m-%d')
            if period == 'monthly':
                record["year"] = int(item.year)
                record["month"] = int(item.month)
            stats.append(record)
            
        return {
            "site_id": site_id, 
            "period": period, 
            "count_periods": count_periods, 
            "statistics": stats
        }, 200

# How many appointments have been made in a site
class SiteStatistics(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('site_id', type=int, required=True, location='args', help="site_id is required")
    parser.add_argument('period', type=str, required=False, default='total', location='args', help="Period can be total, daily, weekly, monthly")
    parser.add_argument('count_periods', type=int, required=False, default=0, location='args', help="Number of days/weeks/months to include from current date backwards if > 0")
    
    # @jwt_required()
    def get(self):
        args = SiteStatistics.parser.parse_args()
        site_id = args['site_id']
        period = args['period'].lower()
        count_periods = args['count_periods']
        
        now = datetime.now()
        
        # Calcular la fecha de inicio según el período y count_periods
        if count_periods > 0:
            if period == 'daily':
                start_date = now - relativedelta(days=count_periods)
            elif period == 'weekly':
                start_date = now - relativedelta(weeks=count_periods)
            elif period == 'monthly':
                start_date = now - relativedelta(months=count_periods)
            else:
                start_date = None
        else:
            start_date = None
        
        base_query = AppointmentModel.query.filter(AppointmentModel.site_id == site_id)
        if start_date:
            base_query = base_query.filter(AppointmentModel.appointmenttime >= start_date, AppointmentModel.appointmenttime <= now)
        
        # Consultas según el período
        if period == 'total':
            total = base_query.count()
            stats = {"total": total}
        elif period == 'daily':
            results = (
                base_query
                .with_entities(
                    func.date(AppointmentModel.appointmenttime).label("day"),
                    func.count(AppointmentModel.id).label("total")
                )
                .group_by(func.date(AppointmentModel.appointmenttime))
                .all()
            )
            stats = [{"day": r.day.strftime('%Y-%m-%d'), "total": r.total} for r in results]
        elif period == 'weekly':
            results = (
                base_query
                .with_entities(
                    func.date_trunc('week', AppointmentModel.appointmenttime).label("week_start"),
                    func.count(AppointmentModel.id).label("total")
                )
                .group_by(func.date_trunc('week', AppointmentModel.appointmenttime))
                .all()
            )
            stats = [{"week_start": r.week_start.strftime('%Y-%m-%d'), "total": r.total} for r in results]
        elif period == 'monthly':
            results = (
                base_query
                .with_entities(
                    func.extract('year', AppointmentModel.appointmenttime).label("year"),
                    func.extract('month', AppointmentModel.appointmenttime).label("month"),
                    func.count(AppointmentModel.id).label("total")
                )
                .group_by(
                    func.extract('year', AppointmentModel.appointmenttime),
                    func.extract('month', AppointmentModel.appointmenttime)
                )
                .all()
            )
            stats = [{"year": int(r.year), "month": int(r.month), "total": r.total} for r in results]
        else:
            return {"message": "Invalid period parameter. Use total, daily, weekly or monthly"}, 400
        
        return {
            "site_id": site_id, 
            "period": period, 
            "count_periods": count_periods, 
            "statistics": stats
        }, 200

# How many appointments have been made for each service in a site
class ServiceStatistics(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('site_id', type=int, required=True, location='args', help="site_id is required")
    parser.add_argument('period', type=str, required=False, default='total', location='args', help="Period can be total, daily, monthly")
    parser.add_argument('count_periods', type=int, required=False, default=0, location='args', help="Number of days/months to include from current date backwards if > 0")
    
    # @jwt_required()
    def get(self):
        args = ServiceStatistics.parser.parse_args()
        site_id = args['site_id']
        period = args['period'].lower()
        count_periods = args['count_periods']
        
        now = datetime.now()
        
        # Calcular la fecha de inicio según el período y count_periods
        if count_periods > 0:
            if period == 'daily':
                start_date = now - relativedelta(days=count_periods)
            elif period == 'monthly':
                start_date = now - relativedelta(months=count_periods)
            else:
                start_date = None
        else:
            start_date = None
        
        base_query = AppointmentModel.query.filter(AppointmentModel.site_id == site_id)
        if start_date:
            base_query = base_query.filter(AppointmentModel.appointmenttime >= start_date, AppointmentModel.appointmenttime <= now)
        
        if period == 'total':
            results = (
                base_query
                .with_entities(AppointmentModel.service_id, func.count(AppointmentModel.id).label("total"))
                .group_by(AppointmentModel.service_id)
                .all()
            )
        elif period == 'daily':
            results = (
                base_query
                .with_entities(
                    AppointmentModel.service_id,
                    func.date(AppointmentModel.appointmenttime).label("day"),
                    func.count(AppointmentModel.id).label("total")
                )
                .group_by(AppointmentModel.service_id, func.date(AppointmentModel.appointmenttime))
                .all()
            )
        elif period == 'monthly':
            results = (
                base_query
                .with_entities(
                    AppointmentModel.service_id,
                    func.extract('year', AppointmentModel.appointmenttime).label("year"),
                    func.extract('month', AppointmentModel.appointmenttime).label("month"),
                    func.count(AppointmentModel.id).label("total")
                )
                .group_by(
                    AppointmentModel.service_id,
                    func.extract('year', AppointmentModel.appointmenttime),
                    func.extract('month', AppointmentModel.appointmenttime)
                )
                .all()
            )
        else:
            return {"message": "Invalid period parameter. Use total, daily or monthly"}, 400

        stats = []
        for item in results:
            record = {"service_id": item.service_id, "total": item.total}
            if period == 'daily':
                record["day"] = item.day.strftime('%Y-%m-%d')
            if period == 'monthly':
                record["year"] = int(item.year)
                record["month"] = int(item.month)
            stats.append(record)
            
        return {
            "site_id": site_id,
            "period": period, 
            "count_periods": count_periods, 
            "statistics": stats
        }, 200