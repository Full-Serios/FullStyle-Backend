from models.appointment_model import AppointmentModel
from flask_restful import Resource, reqparse, request
from datetime import datetime
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