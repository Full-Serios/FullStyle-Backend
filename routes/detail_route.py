# Import resources
from services.detail_service import Detail

# Add resources to the API
def add_resources(api):
    api.add_resource(Detail, "/api/detail")