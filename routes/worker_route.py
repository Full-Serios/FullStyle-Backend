# Import resources
from services.worker_service import Worker

# Add resources to the API
def add_resources(api):
    api.add_resource(Worker, "/api/worker")