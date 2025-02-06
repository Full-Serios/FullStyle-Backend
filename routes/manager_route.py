# Import resources
from services.manager_service import Subscription

# Add resources to the API
def add_resources(api):
    api.add_resource(Subscription, "/api/subscription/<int:id>")