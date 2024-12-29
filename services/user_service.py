from models.user_model import UserModel
from datetime import datetime, timezone
from flask_restful import Resource, reqparse
import utils.encryption as encryption
import bcrypt
from models.token_blocklist_model import TokenBlockListModel
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    create_refresh_token,
    get_jwt,
)

class User(Resource):
    # @jwt_required()
    def get(self):
        users = UserModel.get_all_users()

        if users:
            users_json = [user.json() for user in users]
            return users_json, 200
        return {"message": "User not found"}, 404

class UserRegister(Resource):
    # @jwt_required()
    def get(self):
        users = UserModel.get_all_users()

        if users:
            users_json = [user.json() for user in users]
            return users_json, 200
        return {"message": "User not found"}, 404


class UserLogin(Resource):
    # @jwt_required()
    def get(self):
        users = UserModel.get_all_users()

        if users:
            users_json = [user.json() for user in users]
            return users_json, 200
        return {"message": "User not found"}, 404


class UserLogout(Resource):
    # @jwt_required()
    def get(self):
        users = UserModel.get_all_users()

        if users:
            users_json = [user.json() for user in users]
            return users_json, 200
        return {"message": "User not found"}, 404
    
    
class Test(Resource):
    def get(self):
        return {"message": "Test passed"}, 200