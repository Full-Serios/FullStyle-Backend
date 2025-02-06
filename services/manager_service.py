from models.manager_model import ManagerModel
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    create_refresh_token,
    get_jwt,
)
from config.db_config import db

class Subscription(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "subscriptionactive",
        type=bool,
        required=True,
        help="Subscription status is required."
    )

    # @jwt_required()
    def get(self, id):
        manager = ManagerModel.find_by_id(id)
        if not manager:
            return {"message": "Manager not found"}, 404
        
        return {
            "id": manager.id,
            "subscriptionactive": manager.subscriptionactive
        }, 200

    # @jwt_required()
    def put(self, id):
        data = Subscription.parser.parse_args()
        manager = ManagerModel.find_by_id(id)
        
        if not manager:
            return {"message": "Manager not found"}, 404

        try:
            with db.session.begin_nested():
                manager.subscriptionactive = data["subscriptionactive"]
                db.session.add(manager)
            
            db.session.commit()
            
            return {
                "manager": manager.json()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {"message": f"An error occurred updating the subscription: {str(e)}"}, 500