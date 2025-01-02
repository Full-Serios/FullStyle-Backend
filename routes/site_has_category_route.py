# Import resources
from services.site_has_category_service import SiteHasCategory

# Add resources to the API
def add_resources(api):
    api.add_resource(SiteHasCategory, "/api/site_has_category")