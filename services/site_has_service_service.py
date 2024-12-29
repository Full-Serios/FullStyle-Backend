from models.site_has_service_model import SiteHasServiceModel
from flask_restful import Resource

class SiteHasService(Resource):
    # @jwt_required()
    def get(self):
        site_services = SiteHasServiceModel.get_all_site_services()

        if site_services:
            site_services_json = [site_service.json() for site_service in site_services]
            return site_services_json, 200
        return {"message": "Site-Has-Service not found"}, 404