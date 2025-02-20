from models.notification_model import NotificationModel
from models.appointment_model import AppointmentModel
from flask_restful import Resource, reqparse, request
from utils.helpers import check_appointment_exists

class Notification(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=int, required=False)
    parser.add_argument('type', type=str, required=True, help="This field cannot be left blank!")
    parser.add_argument('status', type=str, required=False, default='pending')
    parser.add_argument('appointment_id', type=int, required=True, help="This field cannot be left blank!")

    # @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args', required=False)
        parser.add_argument('status', type=str, location='args', required=False)
        parser.add_argument('appointment_id', type=int, location='args', required=False)
        parser.add_argument('type', type=str, location='args', required=False)
        parser.add_argument('worker_id', type=int, location='args', required=False)
        parser.add_argument('service_id', type=int, location='args', required=False)
        parser.add_argument('site_id', type=int, location='args', required=False)
        args = parser.parse_args()

        query = NotificationModel.query.join(AppointmentModel, NotificationModel.appointment_id == AppointmentModel.id)

        if args['id']:
            query = query.filter(NotificationModel.id == args['id'])
        if args['status']:
            query = query.filter(NotificationModel.status == args['status'])
        if args['appointment_id']:
            query = query.filter(NotificationModel.appointment_id == args['appointment_id'])
        if args['type']:
            query = query.filter(NotificationModel.type == args['type'])
        if args['worker_id']:
            query = query.filter(AppointmentModel.worker_id == args['worker_id'])
        if args['service_id']:
            query = query.filter(AppointmentModel.service_id == args['service_id'])
        if args['site_id']:
            query = query.filter(AppointmentModel.site_id == args['site_id'])

        notifications = query.all()

        if notifications:
            notifications_json = []
            for notification in notifications:
                notif_data = notification.json()
                if notification.appointment:
                    notif_data.update({
                        "worker_id": notification.appointment.worker_id,
                        "service_id": notification.appointment.service_id,
                        "site_id": notification.appointment.site_id
                    })
                notifications_json.append(notif_data)
            return notifications_json, 200
        return {"message": "Notification not found"}, 404

    # @jwt_required()
    def post(self):
        data = Notification.parser.parse_args()

        _, error = check_appointment_exists(data['appointment_id'])
        if error:
            return {"message": error}, 404

        notification = NotificationModel(
            type=data['type'],
            status=data['status'],
            appointment_id=data['appointment_id']
        )
        try:
            notification.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred inserting the notification: {str(e)}"}, 500
        return notification.json(), 201

    # @jwt_required()
    def put(self):
        data = Notification.parser.parse_args()
        notification_id = data['id']
        if not notification_id:
            return {"message": "Notification ID is required"}, 400

        notification = NotificationModel.find_by_id(notification_id)
        if not notification:
            return {"message": "Notification not found"}, 404

        _, error = check_appointment_exists(data['appointment_id'])
        if error:
            return {"message": error}, 404

        notification.type = data['type']
        notification.status = data['status']
        notification.appointment_id = data['appointment_id']

        try:
            notification.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred updating the notification: {str(e)}"}, 500
        return notification.json(), 200

    # @jwt_required()
    def delete(self):
        notification_id = request.args.get('id')
        if not notification_id:
            return {"message": "Notification ID is required as a query parameter"}, 400

        notification = NotificationModel.find_by_id(notification_id)
        if not notification:
            return {"message": "Notification not found"}, 404

        _, error = check_appointment_exists(notification.appointment_id)
        if error:
            return {"message": error}, 404

        try:
            notification.delete_from_db()
        except Exception as e:
            return {"message": f"An error occurred deleting the notification: {str(e)}"}, 500
        return {"message": "Notification deleted"}, 200