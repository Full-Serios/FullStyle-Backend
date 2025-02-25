from models.appointment_model import AppointmentModel
from models.site_model import SiteModel
from models.detail_model import DetailModel
from models.service_model import ServiceModel
from flask_restful import Resource, reqparse, request
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import func
from utils.helpers import (
    check_appointment_time,
    check_appointment_exists,
    is_worker_available,
    compute_appointment_statistics
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

class AppointmentDetail(Resource):
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

        if not appointments:
            return {"message": "Appointment not found"}, 404

        appointments_json = []
        for appt in appointments:
            # Start with the appointment data
            data = appt.json()
            # Save the id values before removing them
            worker_id = data.get("worker_id")
            site_id   = data.get("site_id")
            service_id = data.get("service_id")
            data.pop("worker_id", None)
            data.pop("site_id", None)
            data.pop("service_id", None)

            # Expand worker attributes using the relationship
            data["worker"] = appt.worker.json() if appt.worker else {}

            # Query for the site information
            site = SiteModel.query.filter_by(id=site_id).first()
            data["site"] = site.json() if site and hasattr(site, "json") else {}

            # Query for the service information
            detail = DetailModel.query.filter_by(site_id=site_id, service_id=service_id).first()
            service_data = detail.json() if detail and hasattr(detail, "json") else {}
            service = ServiceModel.find_by_id(service_id)
            if service:
                service_data = {"name": service.name, **service_data}
            data["service"] = service_data

            appointments_json.append(data)

        return appointments_json, 200

# How many appointments have been made with an specific worker in a site
class AppointmentWorkerStatistics(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('site_id', type=int, required=True, location='args', help="site_id is required")
    parser.add_argument('period', type=str, required=False, default='total', location='args', help="Period can be total, daily, weekly, monthly")
    parser.add_argument('count_periods', type=int, required=False, default=0, location='args', help="Number of days/weeks/months to include from current date backwards if > 0")
    
    # @jwt_required()
    def get(self):
        args = AppointmentWorkerStatistics.parser.parse_args()
        site_id = args['site_id']
        period = args['period'].lower()
        count_periods = args['count_periods']
        
        results = compute_appointment_statistics(site_id, period, count_periods, AppointmentModel.worker_id)
        
        # Format results
        stats = []
        if period == 'total' and type(results) is dict:
            stats = results 
        else:
            for item in results:
                record = {"worker_id": item.worker_id, "total": item.total}
                if period == 'daily':
                    record["day"] = item.day.strftime('%Y-%m-%d')
                elif period == 'weekly':
                    record["week_start"] = item.week_start.strftime('%Y-%m-%d')
                elif period == 'monthly':
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
class AppointmentSiteStatistics(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('site_id', type=int, required=True, location='args', help="site_id is required")
    parser.add_argument('period', type=str, required=False, default='total', location='args', help="Period can be total, daily, weekly, or monthly")
    parser.add_argument('count_periods', type=int, required=False, default=0, location='args', help="Number of days/weeks/months to include from current date backwards if > 0")

    # @jwt_required()
    def get(self):
        args = AppointmentSiteStatistics.parser.parse_args()
        site_id = args['site_id']
        period = args['period'].lower()
        count_periods = args['count_periods']

        results = compute_appointment_statistics(site_id, period, count_periods, group_column=None)

        # Format results
        if period == 'total' and isinstance(results, dict):
            stats = results
        elif period == 'daily':
            stats = [{"day": r.day.strftime('%Y-%m-%d'), "total": r.total} for r in results]
        elif period == 'weekly':
            stats = [{"week_start": r.week_start.strftime('%Y-%m-%d'), "total": r.total} for r in results]
        elif period == 'monthly':
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
class AppointmentServiceStatistics(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('site_id', type=int, required=True, location='args', help="site_id is required")
    parser.add_argument('period', type=str, required=False, default='total', location='args', help="Period can be total, daily, weekly, or monthly")
    parser.add_argument('count_periods', type=int, required=False, default=0, location='args', help="Number of days/weeks/months to include from current date backwards if > 0")
    
    # @jwt_required()
    def get(self):
        args = AppointmentServiceStatistics.parser.parse_args()
        site_id = args['site_id']
        period = args['period'].lower()
        count_periods = args['count_periods']
        
        results = compute_appointment_statistics(site_id, period, count_periods, AppointmentModel.service_id)

        # Format results
        if period == 'total' and isinstance(results, dict):
            stats = results
        elif period == 'daily':
            stats = [{
                "service_id": r.service_id,
                "day": r.day.strftime('%Y-%m-%d'),
                "total": r.total
            } for r in results]
        elif period == 'weekly':
            stats = [{
                "service_id": r.service_id,
                "week_start": r.week_start.strftime('%Y-%m-%d'),
                "total": r.total
            } for r in results]
        elif period == 'monthly':
            stats = [{
                "service_id": r.service_id,
                "year": int(r.year),
                "month": int(r.month),
                "total": r.total
            } for r in results]
        else:
            return {"message": "Invalid period parameter. Use total, daily, weekly or monthly"}, 400

        return {
            "site_id": site_id,
            "period": period,
            "count_periods": count_periods,
            "statistics": stats
        }, 200