# Import resources
from services.appointment_service import Appointment, WorkerStatistics, SiteStatistics, ServiceStatistics

# Add resources to the API
def add_resources(api):
    api.add_resource(Appointment, "/api/appointment")
    api.add_resource(WorkerStatistics, "/api/appointment/worker_statistics")
    api.add_resource(SiteStatistics, "/api/appointment/site_statistics")
    api.add_resource(ServiceStatistics, "/api/appointment/service_statistics")