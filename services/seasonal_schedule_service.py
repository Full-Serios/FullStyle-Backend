from models.seasonal_schedule_model import SeasonalScheduleModel
from flask_restful import Resource, reqparse, request

class SeasonalSchedule(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=int, required=False)
    parser.add_argument('worker_id', type=int, required=True, help="This field cannot be left blank!")
    parser.add_argument('seasonname', type=str, required=True, help="This field cannot be left blank!")
    parser.add_argument('startdate', type=str, required=True, help="This field cannot be left blank!")
    parser.add_argument('enddate', type=str, required=True, help="This field cannot be left blank!")
    parser.add_argument('starttime', type=str, required=True, help="This field cannot be left blank!")
    parser.add_argument('endtime', type=str, required=True, help="This field cannot be left blank!")

    # @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args', required=False)
        parser.add_argument('worker_id', type=int, location='args', required=False)
        parser.add_argument('seasonname', type=str, location='args', required=False)
        args = parser.parse_args()

        query = SeasonalScheduleModel.query

        if args['id']:
            query = query.filter_by(id=args['id'])

        if args['worker_id']:
            query = query.filter_by(worker_id=args['worker_id'])

        if args['seasonname']:
            query = query.filter(SeasonalScheduleModel.seasonname.ilike(f"%{args['seasonname']}%"))

        seasonal_schedules = query.all()

        if seasonal_schedules:
            seasonal_schedules_json = [seasonal_schedule.json() for seasonal_schedule in seasonal_schedules]
            return seasonal_schedules_json, 200
        return {"message": "Seasonal schedule not found"}, 404

    # @jwt_required()
    def post(self):
        data = SeasonalSchedule.parser.parse_args()
        seasonal_schedule = SeasonalScheduleModel(
            worker_id=data['worker_id'],
            seasonname=data['seasonname'],
            startdate=data['startdate'],
            enddate=data['enddate'],
            starttime=data['starttime'],
            endtime=data['endtime']
        )
        try:
            seasonal_schedule.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred inserting the seasonal schedule: {str(e)}"}, 500

        return seasonal_schedule.json(), 201

    # @jwt_required()
    def put(self):
        data = SeasonalSchedule.parser.parse_args()
        seasonal_schedule_id = data['id']

        if not seasonal_schedule_id:
            return {"message": "seasonal_schedule ID is required"}, 400

        seasonal_schedule = SeasonalScheduleModel.query.filter_by(id=seasonal_schedule_id).first()

        if seasonal_schedule:
            seasonal_schedule.seasonname = data['seasonname']
            seasonal_schedule.startdate = data['startdate']
            seasonal_schedule.enddate = data['enddate']
            seasonal_schedule.starttime = data['starttime']
            seasonal_schedule.endtime = data['endtime']
        else:
            return {"message": "Seasonal schedule not found"}, 404

        try:
            seasonal_schedule.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred updating the seasonal schedule: {str(e)}"}, 500

        return seasonal_schedule.json(), 200

    # @jwt_required()
    def delete(self):
        seasonal_schedule_id = request.args.get('id')

        if not seasonal_schedule_id:
            return {"message": "Seasonal schedule ID is required as a query parameter"}, 400

        seasonal_schedule = SeasonalScheduleModel.query.filter_by(id=seasonal_schedule_id).first()

        if seasonal_schedule:
            try:
                seasonal_schedule.delete_from_db()
            except Exception as e:
                return {"message": f"An error occurred deleting the seasonal schedule: {str(e)}"}, 500
            return {"message": "Seasonal schedule deleted"}, 200
        return {"message": "Seasonal schedule not found"}, 404