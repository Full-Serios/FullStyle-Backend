from models.service_model import ServiceModel
from flask_restful import Resource, reqparse

class Service(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help="This field cannot be left blank!")
    parser.add_argument('description', type=str, required=False)
    parser.add_argument('price', type=float, required=True, help="This field cannot be left blank!")
    parser.add_argument('duration', type=int, required=True, help="This field cannot be left blank!")

    ALLOWED_NAMES = {'Corte corriente','Corte sencillo','Corte rapido','Corte con exfoliante','Corte con extenso',
                     'Corte con difuminado','Mascara y exfoliante','Corte y Barba','Corte y barba extenso',
                     'Corte con lavado','Barba y exfoliante','Barba rapida','Corte extenso con lavado','Mascara',
                     'Barba con lavado','Solo barba','Mascara con lavado','Corte y barba con lavado','Manicure','Pedicure'}
    
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
        if data['name'] not in Service.ALLOWED_NAMES:
            return {"message": f"Service name must be one of {Service.ALLOWED_NAMES}"}, 400

        service = ServiceModel(None, data['name'], data['description'], data['price'], data['duration'])
        try:
            service.save_to_db()
        except:
            return {"message": "An error occurred inserting the service."}, 500

        return service.json(), 201

class ServiceNames(Resource):
    def get(self):
        return list(Service.ALLOWED_NAMES), 200