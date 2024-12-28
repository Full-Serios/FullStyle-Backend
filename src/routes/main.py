from flask import Blueprint, jsonify
from src.services.SERVICIO_service import get_all_services
from src.utils.helpers import convert_row_to_dict

main = Blueprint('main', __name__)

@main.route("/")
def home():
    servicios = get_all_services()
    data = [convert_row_to_dict(servicio, servicio._fields) for servicio in servicios]
    return jsonify(data)