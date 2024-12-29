from routes.auth_route import add_resources as add_auth_resources
from routes.service_route import add_resources as add_service_resources

def start_routes(api):
    add_auth_resources(api)
    add_service_resources(api)