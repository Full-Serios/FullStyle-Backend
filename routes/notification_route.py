# Import resources
from services.notification_service import Notification

# Add resources to the API
def add_resources(api):
    api.add_resource(Notification, "/api/notification")