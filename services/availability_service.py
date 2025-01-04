from models.availability_model import AvailabilityModel
from flask_restful import Resource, reqparse, request

class Availability(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=int, required=False)
    parser.add_argument('worker_id', type=int, required=True, help="This field cannot be left blank!")
    parser.add_argument('weekday', type=str, required=True, help="This field cannot be left blank!")
    parser.add_argument('starttime', type=str, required=True, help="This field cannot be left blank!")
    parser.add_argument('endtime', type=str, required=True, help="This field cannot be left blank!")

    # @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args', required=False)
        parser.add_argument('worker_id', type=int, location='args', required=False)
        parser.add_argument('weekday', type=str, location='args', required=False)
        args = parser.parse_args()

        query = AvailabilityModel.query

        if args['id']:
            query = query.filter_by(id=args['id'])

        if args['worker_id']:
            query = query.filter_by(worker_id=args['worker_id'])

        if args['weekday']:
            query = query.filter_by(weekday=args['weekday'])

        availabilities = query.all()

        if availabilities:
            availabilities_json = [availability.json() for availability in availabilities]
            return availabilities_json, 200
        return {"message": "Availability not found"}, 404

    # @jwt_required()
    def post(self):
        data = Availability.parser.parse_args()
        availability = AvailabilityModel(data['worker_id'], data['weekday'], data['starttime'], data['endtime'])
        try:
            availability.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred inserting the availability: {str(e)}"}, 500

        return availability.json(), 201

    # @jwt_required()
    def put(self):
        data = Availability.parser.parse_args()
        availability_id = data['id']

        if not availability_id:
            return {"message": "Availability ID is required"}, 400

        availability = AvailabilityModel.query.filter_by(id=availability_id).first()

        if availability:
            availability.weekday = data['weekday']
            availability.starttime = data['starttime']
            availability.endtime = data['endtime']
        else:
            return {"message": "Availability not found"}, 404

        try:
            availability.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred updating the availability: {str(e)}"}, 500

        return availability.json(), 200

    # @jwt_required()
    def delete(self):
        availability_id = request.args.get('id')

        if not availability_id:
            return {"message": "Availability ID is required as a query parameter"}, 400

        availability = AvailabilityModel.query.filter_by(id=availability_id).first()

        if availability:
            try:
                availability.delete_from_db()
            except Exception as e:
                return {"message": f"An error occurred deleting the availability: {str(e)}"}, 500
            return {"message": "Availability deleted"}, 200
        return {"message": "Availability not found"}, 404