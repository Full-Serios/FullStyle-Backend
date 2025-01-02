# Import resources
from services.service_service import Service, ServiceByQuery

# Add resources to the API
def add_resources(api):
    api.add_resource(Service, "/api/service")
    api.add_resource(ServiceByQuery, "/api/service/query")