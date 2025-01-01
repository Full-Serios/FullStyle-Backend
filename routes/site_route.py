# Import resources
from services.site_service import Site

# Add resources to the API
def add_resources(api):
    api.add_resource(Site, "/api/site")