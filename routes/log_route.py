from services.log_service import GetLogs

def add_resources(api):
    api.add_resource(GetLogs, "/api/logs")