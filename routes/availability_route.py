# Import resources
from services.availability_service import Availability

# Add resources to the API
def add_resources(api):
    api.add_resource(Availability, "/api/availability")