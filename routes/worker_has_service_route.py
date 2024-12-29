# Import resources
from services.worker_has_service_service import WorkerHasService

# Add resources to the API
def add_resources(api):
    api.add_resource(WorkerHasService, "/api/worker_has_service")