from models.site_model import SiteModel
from models.site_has_category_model import SiteHasCategoryModel
from models.detail_model import DetailModel
from flask_restful import Resource, reqparse, request
from utils.helpers import (
    check_site_exists,
    check_manager_exists,
    check_phone
)

class Site(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=int, required=False)
    parser.add_argument('name', type=str, required=False)
    parser.add_argument('address', type=str, required=False)
    parser.add_argument('phone', type=int, required=False)
    parser.add_argument('manager_id', type=int, required=False)
    parser.add_argument('category_id', type=int, required=False)
    parser.add_argument('service_id', type=int, required=False)
    parser.add_argument('photos', type=dict, required=False, help="This field must be a valid JSON object")

    @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args', required=False)
        parser.add_argument('name', type=str, location='args', required=False)
        parser.add_argument('address', type=str, location='args', required=False)
        parser.add_argument('manager_id', type=int, location='args', required=False)
        parser.add_argument('category_id', type=int, location='args', required=False)
        parser.add_argument('service_id', type=int, location='args', required=False)
        args = parser.parse_args()

        query = SiteModel.query

        if args['id']:
            query = query.filter_by(id=args['id'])

        if args['name']:
            query = query.filter(SiteModel.name.ilike(f"%{args['name']}%"))

        if args['address']:
            query = query.filter(SiteModel.address.ilike(f"%{args['address']}%"))

        if args['manager_id']:
            query = query.filter_by(manager_id=args['manager_id'])

        if args['category_id']:
            site_ids = [shc.site_id for shc in SiteHasCategoryModel.query.filter_by(category_id=args['category_id']).all()]
            query = query.filter(SiteModel.id.in_(site_ids))

        if args['service_id']:
            site_ids = [shs.site_id for shs in DetailModel.query.filter_by(service_id=args['service_id']).all()]
            query = query.filter(SiteModel.id.in_(site_ids))

        sites = query.all()

        if sites:
            sites_json = [site.json() for site in sites]
            return sites_json, 200
        return {"message": "Site not found"}, 404

    @jwt_required()
    def post(self):
        data = Site.parser.parse_args()

        # Validate phone number
        valid, error = check_phone(data['phone'])
        if not valid:
            return {"message": error}, 400

        # Check if manager exists
        if data['manager_id']:
            manager, error = check_manager_exists(data['manager_id'])
            if error:
                return {"message": error}, 400

        site = SiteModel(None, data['name'], data['address'], data['phone'], data['manager_id'], data['photos'])
        try:
            site.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred inserting the site: {str(e)}"}, 500

        return site.json(), 201

    @jwt_required()
    def put(self):
        data = Site.parser.parse_args()
        site_id = request.args.get('id')

        if not site_id:
            return {"message": "Site ID is required as a query parameter"}, 400

        site, error = check_site_exists(site_id)
        if error:
            return {"message": error}, 404

        # Validate phone number
        valid, error = check_phone(data['phone'])
        if not valid:
            return {"message": error}, 400

        # Check if manager exists
        if data['manager_id']:
            manager, error = check_manager_exists(data['manager_id'])
            if error:
                return {"message": error}, 400

        site.name = data['name']
        site.address = data['address']
        site.phone = data['phone']
        site.manager_id = data['manager_id']
        site.photos = data['photos']

        try:
            site.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred updating the site: {str(e)}"}, 500

        return site.json(), 200

    @jwt_required()
    def delete(self):
        site_id = request.args.get('id')

        if not site_id:
            return {"message": "Site ID is required as a query parameter"}, 400

        site, error = check_site_exists(site_id)
        if error:
            return {"message": error}, 404

        try:
            site.delete_from_db()
        except Exception as e:
            return {"message": f"An error occurred deleting the site: {str(e)}"}, 500
        return {"message": "Site deleted"}, 200