# Import resources
from services.user_service import User, ResetPasswordRequest, ResetPasswordConfirm

# Add resources to the API
def add_resources(api):
    api.add_resource(User, "/api/user/<int:id>")
    api.add_resource(ResetPasswordRequest, "/api/user/reset-password-request")
    api.add_resource(ResetPasswordConfirm, "/api/user/reset-password")
