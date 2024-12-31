from models.site_model import SiteModel
from flask_restful import Resource, reqparse

class Site(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help="This field cannot be left blank!")
    parser.add_argument('address', type=str, required=True, help="This field cannot be left blank!")
    parser.add_argument('phone', type=str, required=False)
    parser.add_argument('manager_id', type=int, required=True, help="This field cannot be left blank!")
    
    # @jwt_required()
    def get(self):
        sites = SiteModel.get_all_sites()

        if sites:
            sites_json = [site.json() for site in sites]
            return sites_json, 200
        return {"message": "Site not found"}, 404
    
    # @jwt_required()
    def post(self):
        data = Site.parser.parse_args()
        site = SiteModel(None, data['name'], data['address'], data['phone'], data['manager_id'])
        try:
            site.save_to_db()
        except:
            return {"message": "An error occurred inserting the site."}, 500

        return site.json(), 201