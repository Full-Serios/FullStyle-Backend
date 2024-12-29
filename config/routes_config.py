from routes.auth_route import add_resources as add_auth_resources
from routes.service_route import add_resources as add_service_resources
from routes.site_route import add_resources as add_site_resources
from routes.worker_route import add_resources as add_worker_resources
from routes.worker_has_service_route import add_resources as add_worker_has_service_resources
from routes.site_has_service_route import add_resources as add_site_has_service_resources

def start_routes(api):
    add_auth_resources(api)
    add_service_resources(api)
    add_site_resources(api)
    add_worker_resources(api)
    add_worker_has_service_resources(api)
    add_site_has_service_resources(api)