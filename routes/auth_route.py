# Import resources
from services.user_service import UserRegister, UserLogin, UserLogout, Test, RegisterGoogle, LoginGoogle, ManagerRegister
# , LoginGoogle, AuthCallback
# Add resources to the API
def add_resources(api):
    api.add_resource(UserLogin, "/api/login")
    api.add_resource(UserRegister, "/api/register")
    api.add_resource(ManagerRegister, "/api/manager_register")
    api.add_resource(UserLogout, "/api/logout")
    api.add_resource(Test, "/api/test")
    api.add_resource(RegisterGoogle, "/api/register_google")
    api.add_resource(LoginGoogle, "/api/login_google")