# Import resources
from services.days_off_service import DaysOff

# Add resources to the API
def add_resources(api):
    api.add_resource(DaysOff, "/api/days_off")