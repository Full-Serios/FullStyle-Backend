# Import resources
from services.site_has_service_service import SiteHasService

# Add resources to the API
def add_resources(api):
    api.add_resource(SiteHasService, "/api/site_has_service")