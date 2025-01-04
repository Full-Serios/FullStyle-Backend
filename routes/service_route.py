# Import resources
from services.service_service import Service

# Add resources to the API
def add_resources(api):
    api.add_resource(Service, "/api/service")