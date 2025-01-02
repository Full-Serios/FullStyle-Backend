from models.service_model import ServiceModel
from models.category_model import CategoryModel
from flask_restful import Resource, reqparse

class Service(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=int, required=False)
    parser.add_argument('name', type=str, required=True, help="This field cannot be left blank!")
    parser.add_argument('description', type=str, required=False)
    parser.add_argument('price', type=float, required=True, help="This field cannot be left blank!")
    parser.add_argument('duration', type=int, required=True, help="This field cannot be left blank!")
    parser.add_argument('category_id', type=int, required=True, help="This field cannot be left blank!")

    # @jwt_required()
    def get(self):
        services = ServiceModel.get_all_services()

        if services:
            services_json = [service.json() for service in services]
            return services_json, 200
        return {"message": "Service not found"}, 404

    # @jwt_required()
    def post(self):
        data = Service.parser.parse_args()
        category = CategoryModel.query.filter_by(id=data['category_id']).first()
        if not category:
            return {"message": "Invalid category ID"}, 400

        service = ServiceModel(data['id'], data['name'], data['description'], data['price'], data['duration'], data['category_id'])
        try:
            service.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred inserting the service: {str(e)}"}, 500

        return service.json(), 201

class ServiceByQuery(Resource):
    # @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args', required=False)
        parser.add_argument('name', type=str, location='args', required=False)
        parser.add_argument('category_id', type=int, location='args', required=False)
        args = parser.parse_args()

        if args['id']:
            service = ServiceModel.find_by_id(args['id'])
            if service:
                return service.json(), 200
            return {"message": "Service not found"}, 404

        if args['name']:
            service = ServiceModel.find_by_name(args['name'])
            if service:
                return service.json(), 200
            return {"message": "Service not found"}, 404

        if args['category_id']:
            services = ServiceModel.find_by_category(args['category_id'])
            if services:
                services_json = [service.json() for service in services]
                return services_json, 200
            return {"message": "No services found for this category"}, 404

        return {"message": "No query parameters provided"}, 400