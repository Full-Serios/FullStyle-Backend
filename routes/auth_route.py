# Import resources
from services.user_service import User, UserRegister, UserLogin, UserLogout, Test

# Add resources to the API
def add_resources(api):
    api.add_resource(User, "/api/user")
    api.add_resource(UserLogin, "/api/login")
    api.add_resource(UserRegister, "/api/register")
    api.add_resource(UserLogout, "/api/logout")
    api.add_resource(Test, "/api/test")