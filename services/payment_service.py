from models.payment_model import PaymentModel
from models.appointment_model import AppointmentModel
from flask_restful import Resource, reqparse, request
from utils.helpers import check_appointment_exists, compute_payment_statistics

class Payment(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=int, required=False)
    parser.add_argument('amount', type=int, required=True, help="This field cannot be left blank!")
    parser.add_argument('paymentmethod', type=str, required=True, help="This field cannot be left blank!")
    parser.add_argument('status', type=str, required=False, default='pending')
    parser.add_argument('appointment_id', type=int, required=True, help="This field cannot be left blank!")

    @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args', required=False)
        parser.add_argument('status', type=str, location='args', required=False)
        parser.add_argument('appointment_id', type=int, location='args', required=False)
        parser.add_argument('amount', type=int, location='args', required=False, help="Return payments with amount less or equal to this value")
        parser.add_argument('paymentmethod', type=str, location='args', required=False)
        parser.add_argument('worker_id', type=int, location='args', required=False)
        parser.add_argument('service_id', type=int, location='args', required=False)
        parser.add_argument('site_id', type=int, location='args', required=False)
        args = parser.parse_args()

        query = PaymentModel.query.join(AppointmentModel, PaymentModel.appointment_id == AppointmentModel.id)

        if args['id']:
            query = query.filter(PaymentModel.id == args['id'])
        if args['status']:
            query = query.filter(PaymentModel.status == args['status'])
        if args['appointment_id']:
            query = query.filter(PaymentModel.appointment_id == args['appointment_id'])
        if args['amount'] is not None:
            query = query.filter(PaymentModel.amount <= args['amount'])
        if args['paymentmethod']:
            query = query.filter(PaymentModel.paymentmethod == args['paymentmethod'])
        if args['worker_id']:
            query = query.filter(AppointmentModel.worker_id == args['worker_id'])
        if args['service_id']:
            query = query.filter(AppointmentModel.service_id == args['service_id'])
        if args['site_id']:
            query = query.filter(AppointmentModel.site_id == args['site_id'])

        payments = query.all()

        if payments:
            payments_json = []
            for payment in payments:
                payment_data = payment.json()
                if payment.appointment:
                    payment_data.update({
                        "worker_id": payment.appointment.worker_id,
                        "service_id": payment.appointment.service_id,
                        "site_id": payment.appointment.site_id
                    })
                payments_json.append(payment_data)
            return payments_json, 200
        return {"message": "Payment not found"}, 404

    @jwt_required()
    def post(self):
        data = Payment.parser.parse_args()
        payment = PaymentModel(
            amount=data['amount'],
            paymentmethod=data['paymentmethod'],
            status=data['status'],
            appointment_id=data['appointment_id']
        )

        _, error = check_appointment_exists(data['appointment_id'])
        if error:
            return {"message": error}, 404

        try:
            payment.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred inserting the payment: {str(e)}"}, 500
        return payment.json(), 201

    @jwt_required()
    def put(self):
        data = Payment.parser.parse_args()
        payment_id = data['id']
        if not payment_id:
            return {"message": "Payment ID is required"}, 400

        payment = PaymentModel.find_by_id(payment_id)
        if not payment:
            return {"message": "Payment not found"}, 404

        appointment_id = payment.appointment_id
        _, error = check_appointment_exists(appointment_id)
        if error:
            return {"message": error}, 404

        payment.amount = data['amount']
        payment.paymentmethod = data['paymentmethod']
        payment.status = data['status']
        payment.appointment_id = data['appointment_id']

        try:
            payment.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred updating the payment: {str(e)}"}, 500
        return payment.json(), 200

    @jwt_required()
    def delete(self):
        payment_id = request.args.get('id')
        if not payment_id:
            return {"message": "Payment ID is required as a query parameter"}, 400

        payment = PaymentModel.find_by_id(payment_id)
        if not payment:
            return {"message": "Payment not found"}, 404

        appointment_id = payment.appointment_id
        _, error = check_appointment_exists(appointment_id)
        if error:
            return {"message": error}, 404

        try:
            payment.delete_from_db()
        except Exception as e:
            return {"message": f"An error occurred deleting the payment: {str(e)}"}, 500
        return {"message": "Payment deleted"}, 200


class PaymentWorkerStatistics(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('site_id', type=int, required=True, location='args', help="site_id is required")
    parser.add_argument('period', type=str, required=False, default='total', location='args', help="Period can be total, daily, weekly, or monthly")
    parser.add_argument('count_periods', type=int, required=False, default=0, location='args', help="Number of days/weeks/months to include from current date backwards if > 0")

    @jwt_required()
    def get(self):
        args = PaymentWorkerStatistics.parser.parse_args()
        site_id = args['site_id']
        period = args['period'].lower()
        count_periods = args['count_periods']

        results = compute_payment_statistics(site_id, period, count_periods, AppointmentModel.worker_id)

        # Format results
        if period == 'total':
            stats = [{
                "worker_id": r.worker_id,
                "total_amount": r.total_amount
            } for r in results]
        elif period == 'daily':
            stats = [{
                "worker_id": r.worker_id,
                "day": r.day.strftime('%Y-%m-%d'),
                "total_amount": r.total_amount
            } for r in results]
        elif period == 'weekly':
            stats = [{
                "worker_id": r.worker_id,
                "week_start": r.week_start.strftime('%Y-%m-%d'),
                "total_amount": r.total_amount
            } for r in results]
        elif period == 'monthly':
            stats = [{
                "worker_id": r.worker_id,
                "year": int(r.year),
                "month": int(r.month),
                "total_amount": r.total_amount
            } for r in results]
        else:
            return {"message": "Invalid period parameter. Use total, daily, weekly or monthly"}, 400

        return {
            "site_id": site_id,
            "period": period,
            "count_periods": count_periods,
            "statistics": stats
        }, 200


class PaymentSiteStatistics(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('site_id', type=int, required=True, location='args', help="site_id is required")
    parser.add_argument('period', type=str, required=False, default='total', location='args', help="Period can be total, daily, weekly, or monthly")
    parser.add_argument('count_periods', type=int, required=False, default=0, location='args', help="Number of days/weeks/months to include from current date backwards if > 0")

    @jwt_required()
    def get(self):
        args = PaymentSiteStatistics.parser.parse_args()
        site_id = args['site_id']
        period = args['period'].lower()
        count_periods = args['count_periods']

        results = compute_payment_statistics(site_id, period, count_periods, group_column=None)

        # Format results
        if period == 'total' and isinstance(results, dict):
            stats = results
        elif period == 'daily':
            stats = [{
                "day": r.day.strftime('%Y-%m-%d'),
                "total_amount": r.total_amount
            } for r in results]
        elif period == 'weekly':
            stats = [{
                "week_start": r.week_start.strftime('%Y-%m-%d'),
                "total_amount": r.total_amount
            } for r in results]
        elif period == 'monthly':
            stats = [{
                "year": int(r.year),
                "month": int(r.month),
                "total_amount": r.total_amount
            } for r in results]
        else:
            return {"message": "Invalid period parameter. Use total, daily, weekly or monthly"}, 400

        return {
            "site_id": site_id,
            "period": period,
            "count_periods": count_periods,
            "statistics": stats
        }, 200


class PaymentServiceStatistics(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('site_id', type=int, required=True, location='args', help="site_id is required")
    parser.add_argument('period', type=str, required=False, default='total', location='args',
                        help="Period can be total, daily, weekly, or monthly")
    parser.add_argument('count_periods', type=int, required=False, default=0, location='args',
                        help="Number of days/weeks/months to include from current date backwards if > 0")

    @jwt_required()
    def get(self):
        args = PaymentServiceStatistics.parser.parse_args()
        site_id = args['site_id']
        period = args['period'].lower()
        count_periods = args['count_periods']

        results = compute_payment_statistics(site_id, period, count_periods, AppointmentModel.service_id)

        # Format results
        if period == 'total':
            stats = [{
                "service_id": r.service_id,
                "total_amount": r.total_amount
            } for r in results]
        elif period == 'daily':
            stats = [{
                "service_id": r.service_id,
                "day": r.day.strftime('%Y-%m-%d'),
                "total_amount": r.total_amount
            } for r in results]
        elif period == 'weekly':
            stats = [{
                "service_id": r.service_id,
                "week_start": r.week_start.strftime('%Y-%m-%d'),
                "total_amount": r.total_amount
            } for r in results]
        elif period == 'monthly':
            stats = [{
                "service_id": r.service_id,
                "year": int(r.year),
                "month": int(r.month),
                "total_amount": r.total_amount
            } for r in results]
        else:
            return {"message": "Invalid period parameter. Use total, daily, weekly or monthly"}, 400

        return {
            "site_id": site_id,
            "period": period,
            "count_periods": count_periods,
            "statistics": stats
        }, 200