# Import resources
from services.seasonal_schedule_service import SeasonalSchedule

# Add resources to the API
def add_resources(api):
    api.add_resource(SeasonalSchedule, "/api/seasonal_schedule")