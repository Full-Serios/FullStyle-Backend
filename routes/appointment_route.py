# Import resources
from services.appointment_service import Appointment

# Add resources to the API
def add_resources(api):
    api.add_resource(Appointment, "/api/appointment")