from routes.auth_route import add_resources as add_auth_resources
from routes.user_route import add_resources as add_user_resources
from routes.service_route import add_resources as add_service_resources
from routes.site_route import add_resources as add_site_resources
from routes.worker_route import add_resources as add_worker_resources
from routes.worker_has_service_route import add_resources as add_worker_has_service_resources
from routes.site_has_category_route import add_resources as add_site_has_category_resources
from routes.category_route import add_resources as add_category_resources
from routes.detail_route import add_resources as add_detail_resources
from routes.availability_route import add_resources as add_availability_resources
from routes.days_off_route import add_resources as add_days_off_resources
from routes.seasonal_schedule_route import add_resources as add_seasonal_schedule_resources
from routes.appointment_route import add_resources as add_appointment_resources

def start_routes(api):
    add_auth_resources(api)
    add_service_resources(api)
    add_site_resources(api)
    add_worker_resources(api)
    add_worker_has_service_resources(api)
    add_site_has_category_resources(api)
    add_category_resources(api)
    add_detail_resources(api)
    add_availability_resources(api)
    add_days_off_resources(api)
    add_seasonal_schedule_resources(api)
    add_appointment_resources(api)
    add_user_resources(api)