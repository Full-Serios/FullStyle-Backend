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
from datetime import datetime

class Subscription(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "subscriptionactive",
        type=bool,
        required=True,
        help="Subscription status is required."
    )
    parser.add_argument(
        "subscriptionstartdate",
        type=str,
        required=False,
        help="Start date of the subscription (format: YYYY-MM-DDThh:mm:ss)"
    )
    parser.add_argument(
        "subscriptiontype",
        type=str,
        required=False,
        help="Type of subscription"
    )
    parser.add_argument(
        "subscriptionfinishdate",
        type=str,
        required=False,
        help="End date of the subscription (format: YYYY-MM-DDThh:mm:ss)"
    )

    @jwt_required()
    def get(self, id):
        manager = ManagerModel.find_by_id(id)
        if not manager:
            return {"message": "Manager not found"}, 404

        return {
            "id": manager.id,
            "subscriptionactive": manager.subscriptionactive,
            "subscriptionstartdate": manager.subscriptionstartdate.isoformat() if manager.subscriptionstartdate else None,
            "subscriptiontype": manager.subscriptiontype,
            "subscriptionfinishdate": manager.subscriptionfinishdate.isoformat() if manager.subscriptionfinishdate else None
        }, 200

    @jwt_required()
    def put(self, id):
        data = Subscription.parser.parse_args()
        manager = ManagerModel.find_by_id(id)

        if not manager:
            return {"message": "Manager not found"}, 404

        try:
            with db.session.begin_nested():
                manager.subscriptionactive = data["subscriptionactive"]

                # Actualizar fechas si se proporcionan
                if data["subscriptionstartdate"]:
                    manager.subscriptionstartdate = datetime.fromisoformat(data["subscriptionstartdate"])

                if data["subscriptionfinishdate"]:
                    manager.subscriptionfinishdate = datetime.fromisoformat(data["subscriptionfinishdate"])

                # Actualizar tipo de suscripción si se proporciona
                if data["subscriptiontype"]:
                    manager.subscriptiontype = data["subscriptiontype"]

                db.session.add(manager)

            db.session.commit()

            return {
                "manager": manager.json()
            }, 200

        except ValueError as e:
            return {"message": "Invalid date format. Use ISO format (YYYY-MM-DDThh:mm:ss)"}, 400
        except Exception as e:
            db.session.rollback()
            return {"message": f"An error occurred updating the subscription: {str(e)}"}, 500