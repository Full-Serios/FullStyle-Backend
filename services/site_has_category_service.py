from models.site_has_category_model import SiteHasCategoryModel
from flask_restful import Resource, reqparse

class SiteHasCategory(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('site_id', type=int, required=True, help="This field cannot be left blank!")
    parser.add_argument('category_id', type=int, required=True, help="This field cannot be left blank!")

    # @jwt_required()
    def get(self):
        site_categories = SiteHasCategoryModel.get_all_site_categories()

        if site_categories:
            site_categories_json = [site_category.json() for site_category in site_categories]
            return site_categories_json, 200
        return {"message": "Site-Has-Category not found"}, 404

    # @jwt_required()
    def post(self):
        data = SiteHasCategory.parser.parse_args()
        site_category = SiteHasCategoryModel(data['site_id'], data['category_id'])
        try:
            site_category.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred inserting the site-category relationship: {str(e)}"}, 500

        return site_category.json(), 201