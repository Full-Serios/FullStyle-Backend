# Import resources
from services.appointment_service import Appointment, AppointmentDetail, AppointmentWorkerStatistics, AppointmentSiteStatistics, AppointmentServiceStatistics

# Add resources to the API
def add_resources(api):
    api.add_resource(Appointment, "/api/appointment")
    api.add_resource(AppointmentDetail, "/api/appointmentdetail")
    api.add_resource(AppointmentWorkerStatistics, "/api/appointment/worker_statistics")
    api.add_resource(AppointmentSiteStatistics, "/api/appointment/site_statistics")
    api.add_resource(AppointmentServiceStatistics, "/api/appointment/service_statistics")