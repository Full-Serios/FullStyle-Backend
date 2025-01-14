from models.detail_model import DetailModel
from models.service_model import ServiceModel
from models.category_model import CategoryModel
from models.site_model import SiteModel
from flask_restful import Resource, reqparse, request
from flask_jwt_extended import jwt_required
from utils.helpers import (
    check_detail_exists,
    check_detail_active,
    check_price,
    check_duration
)

class Detail(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('site_id', type=int, required=True, help="This field cannot be left blank!")
    parser.add_argument('service_id', type=int, required=True, help="This field cannot be left blank!")
    parser.add_argument('description', type=str, required=False)
    parser.add_argument('price', type=int, required=True, help="This field cannot be left blank! Remember it must be in COP units")
    parser.add_argument('duration', type=int, required=True, help="This field cannot be left blank!")
    parser.add_argument('photos', type=dict, required=False, help="This field must be a valid JSON object")

    @jwt_required()
    def get(self): # category_name, site_name, service_name, site_address
        parser = reqparse.RequestParser()
        parser.add_argument('site_id', type=int, location='args', required=False)
        parser.add_argument('service_id', type=int, location='args', required=False)
        parser.add_argument('price', type=int, location='args', required=False)
        parser.add_argument('name', type=str, location='args', required=False)
        parser.add_argument('category_id', type=int, location='args', required=False)
        args = parser.parse_args()

        query = DetailModel.query.join(ServiceModel, DetailModel.service_id == ServiceModel.id) \
                                 .join(SiteModel, DetailModel.site_id == SiteModel.id) \
                                 .join(CategoryModel, ServiceModel.category_id == CategoryModel.id) \
                                 .filter(DetailModel.active == True)

        if args['price']:
            query = query.filter(DetailModel.price <= args['price'])

        if args['site_id']:
            query = query.filter(DetailModel.site_id == args['site_id'])

        if args['service_id']:
            query = query.filter(DetailModel.service_id == args['service_id'])

        if args['name']:
            query = query.filter(ServiceModel.name.ilike(f"%{args['name']}%"))

        if args['category_id']:
            query = query.filter(ServiceModel.category_id == args['category_id'])

        details = query.all()

        if details:
            details_json = [{
                "site_id": detail.site_id,
                "site_name": detail.site.name,
                "site_address": detail.site.address,
                "category_id": detail.service.category.id,
                "category_name": detail.service.category.name,
                "service_id": detail.service_id,
                "service_name": detail.service.name,
                "price": detail.price,
                "duration": detail.duration,
                "description": detail.description,
                "photos": detail.photos
            } for detail in details]
            return details_json, 200
        return {"message": "Detail not found"}, 404

    @jwt_required()
    def post(self):
        data = Detail.parser.parse_args()

        # Validate price
        valid, error = check_price(data['price'])
        if not valid:
            return {"message": error}, 400

        # Validate duration
        valid, error = check_duration(data['duration'])
        if not valid:
            return {"message": error}, 400

        detail, error = check_detail_active(data['site_id'], data['service_id'])
        if detail:
            return {"message": "Detail already exists and is active"}, 400

        detail, error = check_detail_exists(data['site_id'], data['service_id'])
        if detail:
            detail.active = True
            detail.description = data['description']
            detail.price = data['price']
            detail.duration = data['duration']
            detail.photos = data['photos']
            try:
                detail.save_to_db()
            except Exception as e:
                return {"message": f"An error occurred updating the detail: {str(e)}"}, 500
            return detail.json(), 200
        else:
            detail = DetailModel(
                data['site_id'], 
                data['service_id'], 
                data['description'], 
                data['price'], 
                data['duration'], 
                photos=data['photos']
            )
            try:
                detail.save_to_db()
            except Exception as e:
                return {"message": f"An error occurred inserting the detail: {str(e)}"}, 500

            return detail.json(), 201

    @jwt_required()
    def put(self):
        data = Detail.parser.parse_args()

        # Validate price
        valid, error = check_price(data['price'])
        if not valid:
            return {"message": error}, 400

        # Validate duration
        valid, error = check_duration(data['duration'])
        if not valid:
            return {"message": error}, 400

        detail, error = check_detail_exists(data['site_id'], data['service_id'])
        if error:
            return {"message": error}, 404

        detail.description = data['description']
        detail.price = data['price']
        detail.duration = data['duration']
        detail.photos = data['photos']

        try:
            detail.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred updating the detail: {str(e)}"}, 500

        return detail.json(), 200

    @jwt_required()
    def delete(self):
        site_id = request.args.get('site_id')
        service_id = request.args.get('service_id')

        if not site_id or not service_id:
            return {"message": "Site ID and Service ID are required as query parameters"}, 400

        detail, error = check_detail_exists(site_id, service_id)
        if error:
            return {"message": error}, 404

        try:
            detail.deactivate()
        except Exception as e:
            return {"message": f"An error occurred deactivating the detail: {str(e)}"}, 500
        return {"message": "Detail deactivated"}, 200