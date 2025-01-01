from models.site_model import SiteModel
from flask_restful import Resource

class Site(Resource):
    # @jwt_required()
    def get(self):
        sites = SiteModel.get_all_sites()

        if sites:
            sites_json = [site.json() for site in sites]
            return sites_json, 200
        return {"message": "Site not found"}, 404