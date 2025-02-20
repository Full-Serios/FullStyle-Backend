# Import resources
from services.worker_service import Worker, WorkerWeeklySchedule, WorkerDailySchedule

# Add resources to the API
def add_resources(api):
    api.add_resource(Worker, "/api/worker")
    api.add_resource(WorkerWeeklySchedule, "/api/worker/weekly_schedule")
    api.add_resource(WorkerDailySchedule, "/api/worker/daily_schedule")