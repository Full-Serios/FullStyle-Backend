from models.days_off_model import DaysOffModel
from flask_restful import Resource, reqparse, request

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
        dayoff = DaysOffModel(data['worker_id'], data['dayoff'])
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
            return {"message": "days_off ID is required"}, 400

        days_off = DaysOffModel.query.filter_by(id=days_off_id).first()

        if days_off:
            days_off.worker_id = data['worker_id']
            days_off.dayoff = data['dayoff']
        else:
            return {"message": "Day off not found"}, 404

        try:
            days_off.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred updating the day off: {str(e)}"}, 500

        return days_off.json(), 200

    # @jwt_required()
    def delete(self):
        days_off_id = request.args.get('id')

        if not days_off_id:
            return {"message": "Day Off ID is required as a query parameter"}, 400

        days_off = DaysOffModel.query.filter_by(id=days_off_id).first()

        if days_off:
            try:
                days_off.delete_from_db()
            except Exception as e:
                return {"message": f"An error occurred deleting the day off: {str(e)}"}, 500
            return {"message": "Day off deleted"}, 200
        return {"message": "Day off not found"}, 404