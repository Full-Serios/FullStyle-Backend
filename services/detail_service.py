from models.detail_model import DetailModel
from models.service_model import ServiceModel
from flask_restful import Resource, reqparse, request

class Detail(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('site_id', type=int, required=True, help="This field cannot be left blank!")
    parser.add_argument('service_id', type=int, required=True, help="This field cannot be left blank!")
    parser.add_argument('description', type=str, required=False)
    parser.add_argument('price', type=float, required=True, help="This field cannot be left blank!")
    parser.add_argument('duration', type=int, required=True, help="This field cannot be left blank!")

    # @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('site_id', type=int, location='args', required=False)
        parser.add_argument('service_id', type=int, location='args', required=False)
        parser.add_argument('price', type=float, location='args', required=False)
        args = parser.parse_args()

        query = DetailModel.query.filter_by(active=True)

        if args['price']:
            query = query.filter(DetailModel.price <= args['price'])

        if args['site_id']:
            query = query.filter_by(site_id=args['site_id'])

        if args['service_id']:
            query = query.filter_by(service_id=args['service_id'])

        details = query.all()

        if details:
            details_json = [detail.json() for detail in details]
            return details_json, 200
        return {"message": "Detail not found"}, 404

    # @jwt_required()
    def post(self):
        data = Detail.parser.parse_args()
        detail = DetailModel(data['site_id'], data['service_id'], data['description'], data['price'], data['duration'])
        try:
            detail.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred inserting the detail: {str(e)}"}, 500

        return detail.json(), 201

    # @jwt_required()
    def put(self):
        data = Detail.parser.parse_args()
        detail = DetailModel.find_by_site_and_service(data['site_id'], data['service_id'])

        if detail:
            detail.description = data['description']
            detail.price = data['price']
            detail.duration = data['duration']
        else:
            return {"message": "Detail not found"}, 404

        try:
            detail.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred updating the detail: {str(e)}"}, 500

        return detail.json(), 200

    # @jwt_required()
    def delete(self):
        site_id = request.args.get('site_id')
        service_id = request.args.get('service_id')

        if not site_id or not service_id:
            return {"message": "Site ID and Service ID are required as query parameters"}, 400

        detail = DetailModel.find_by_site_and_service(site_id, service_id)

        if detail:
            try:
                detail.deactivate()
            except Exception as e:
                return {"message": f"An error occurred deactivating the detail: {str(e)}"}, 500
            return {"message": "Detail deactivated"}, 200
        return {"message": "Detail not found"}, 404