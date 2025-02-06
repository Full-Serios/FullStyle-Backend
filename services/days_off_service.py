from models.days_off_model import DaysOffModel
from flask_restful import Resource, reqparse, request
from utils.helpers import (
    check_date,
    check_worker_exists,
    check_worker_active,
    check_dayoff_exists
)

class DaysOff(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=int, required=False)
    parser.add_argument('worker_id', type=int, required=True, help="This field cannot be left blank!")
    parser.add_argument('dayoff', type=str, required=True, help="This field cannot be left blank!")

    # @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args', required=False)
        parser.add_argument('worker_id', type=int, location='args', required=False)
        parser.add_argument('dayoff', type=str, location='args', required=False)
        args = parser.parse_args()

        query = DaysOffModel.query

        if args['id']:
            query = query.filter_by(id=args['id'])

        if args['worker_id']:
            query = query.filter_by(worker_id=args['worker_id'])

        if args['dayoff']:
            query = query.filter_by(dayoff=args['dayoff'])

        days_off = query.all()

        if days_off:
            days_off_json = [dayoff.json() for dayoff in days_off]
            return days_off_json, 200
        return {"message": "Days off not found"}, 404

    # @jwt_required()
    def post(self):
        data = DaysOff.parser.parse_args()

        # Parse dayoff date
        dayoff_date, error = check_date(data['dayoff'])
        if error:
            return {"message": error}, 400

        # Check if worker exists
        worker, error = check_worker_exists(data['worker_id'])
        if error:
            return {"message": error}, 400

        # Check if worker is active
        worker, error = check_worker_active(data['worker_id'])
        if error:
            return {"message": error}, 400

        dayoff = DaysOffModel(data['worker_id'], dayoff_date)
        try:
            dayoff.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred inserting the day off: {str(e)}"}, 500

        return dayoff.json(), 201

    # @jwt_required()
    def put(self):
        data = DaysOff.parser.parse_args()
        days_off_id = data['id']

        if not days_off_id:
            return {"message": "Day off ID is required"}, 400

        dayoff, error = check_dayoff_exists(days_off_id)
        if error:
            return {"message": error}, 404

        # Parse dayoff date
        dayoff_date, error = check_date(data['dayoff'])
        if error:
            return {"message": error}, 400

        # Check if worker exists
        worker, error = check_worker_exists(data['worker_id'])
        if error:
            return {"message": error}, 400

        # Check if worker is active
        worker, error = check_worker_active(data['worker_id'])
        if error:
            return {"message": error}, 400

        dayoff.worker_id = data['worker_id']
        dayoff.dayoff = dayoff_date

        try:
            dayoff.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred updating the day off: {str(e)}"}, 500

        return dayoff.json(), 200

    # @jwt_required()
    def delete(self):
        days_off_id = request.args.get('id')

        if not days_off_id:
            return {"message": "Day off ID is required as a query parameter"}, 400

        dayoff, error = check_dayoff_exists(days_off_id)
        if error:
            return {"message": error}, 404

        try:
            dayoff.delete_from_db()
        except Exception as e:
            return {"message": f"An error occurred deleting the day off: {str(e)}"}, 500
        return {"message": "Day off deleted"}, 200