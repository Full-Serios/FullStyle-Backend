# Import resources
from services.payment_service import Payment, PaymentWorkerStatistics, PaymentSiteStatistics, PaymentServiceStatistics

# Add resources to the API
def add_resources(api):
    api.add_resource(Payment, "/api/payment")
    api.add_resource(PaymentWorkerStatistics, "/api/payment/worker_statistics")
    api.add_resource(PaymentSiteStatistics, "/api/payment/site_statistics")
    api.add_resource(PaymentServiceStatistics, "/api/payment/service_statistics")