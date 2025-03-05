from models.service_model import ServiceModel
from models.category_model import CategoryModel
from flask_restful import Resource, reqparse, request
from utils.helpers import (
    check_category_exists,
    check_service_unique
)
from flask_jwt_extended import jwt_required
class Service(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=int, required=False)
    parser.add_argument('category_id', type=int, required=True, help="This field cannot be left blank!")
    parser.add_argument('name', type=str, required=True, help="This field cannot be left blank!")

    @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args', required=False)
        parser.add_argument('name', type=str, location='args', required=False)
        parser.add_argument('category_id', type=int, location='args', required=False)
        args = parser.parse_args()

        query = ServiceModel.query

        if args['id']:
            query = query.filter_by(id=args['id'])

        if args['name']:
            query = query.filter(ServiceModel.name.ilike(f"{args['name']}%"))

        if args['category_id']:
            query = query.filter_by(category_id=args['category_id'])

        services = query.all()

        if services:
            services_json = [service.json() for service in services]
            return services_json, 200
        return {"message": "Service not found"}, 404

    @jwt_required()
    def post(self):
        data = Service.parser.parse_args()

        # Check if category exists
        category, error = check_category_exists(data['category_id'])
        if error:
            return {"message": error}, 400

        # Check if service is unique
        unique, error = check_service_unique(data['name'], data['category_id'])
        if not unique:
            return {"message": error}, 400

        service = ServiceModel(data['category_id'], data['name'])
        try:
            service.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred inserting the service: {str(e)}"}, 500

        return service.json(), 201