from models.site_has_service_model import SiteHasServiceModel
from flask_restful import Resource, reqparse

class SiteHasService(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('site_id', type=int, required=True, help="This field cannot be left blank!")
    parser.add_argument('site_manager_id', type=int, required=True, help="This field cannot be left blank!")
    parser.add_argument('service_id', type=int, required=True, help="This field cannot be left blank!")

    # @jwt_required()
    def get(self):
        site_services = SiteHasServiceModel.get_all_site_services()

        if site_services:
            site_services_json = [site_service.json() for site_service in site_services]
            return site_services_json, 200
        return {"message": "Site-Has-Service not found"}, 404

    # @jwt_required()
    def post(self):
        data = SiteHasService.parser.parse_args()
        site_service = SiteHasServiceModel(data['site_id'], data['site_manager_id'], data['service_id'])
        try:
            site_service.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred inserting the site-service relationship: {str(e)}"}, 500

        return site_service.json(), 201