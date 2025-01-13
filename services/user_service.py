from models.user_model import UserModel
from models.manager_model import ManagerModel
from datetime import datetime, timezone
from flask_restful import Resource, reqparse
import utils.encryption as encryption
import bcrypt
from werkzeug.security import generate_password_hash
from models.token_blocklist_model import redis_client
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    create_refresh_token,
    get_jwt,
)
from flask import make_response

class User(Resource):
    parser = reqparse.RequestParser()
    # parser.add_argument(
    #     "name", type=str, required=True, help="This field cannot be blank."
    # )
    # parser.add_argument(
    #     "email", type=str, required=True, help="This field cannot be blank."
    # )
    parser.add_argument(
        "password", type=str, required=True, help="This field cannot be blank."
    )

    # @jwt_required()
    def get(self, id):
        user = UserModel.find_by_id(id)

        if user is not None and user.active:
            return user.json(), 200
        return {"message": "User not found"}, 404

    # @jwt_required()
    def put(self, id):
        # current_user = get_jwt_identity()
        # if current_user["id"] != id:
        #     return {"message": "Not found"}, 404

        data = User.parser.parse_args()

        if data["password"] == "" or len(data["password"]) < 8:
            return {"message": "Password must be at least 8 characters"}, 400

        user = UserModel.find_by_id(id)
        if user is None:
            user = UserModel(**data)
        else:
            user.password = generate_password_hash(data["password"], method="pbkdf2")

        try:
            user.save_to_db()
            return user.json(), 200
        except:
            return {"message": "An error occurred updating the user."}, 500

    # @jwt_required()
    def delete(self, id):
        user = UserModel.find_by_id(id)
        if user:
            user.delete_from_db()

        # Obtener información del token actual
        token = get_jwt()
        jti = token["jti"]  # Identificador único del token
        exp = token["exp"]  # Timestamp de expiración
        now = int(datetime.now(timezone.utc).timestamp())
        ttl = exp - now  # Tiempo restante hasta la expiración en segundos

        # Bloquear el token en Redis con el TTL
        try:
            redis_client.setex(jti, ttl, "blocked")  # Almacenar JTI con TTL
            return {"message": "User deleted and token invalidated"}, 200
        except:
            return {"message": "An error occurred deleting the user."}, 500

class RegisterGoogle(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "name", type=str, required=True, help="This field cannot be blank."
    )
    parser.add_argument(
        "email", type=str, required=True, help="This field cannot be blank."
    )

    def post(self):
        data = RegisterGoogle.parser.parse_args()

        if not data:
            return {"error": "No data provided"}, 400

        email = data["email"]

        # Verifica si el usuario ya existe
        existing_user = UserModel.query.filter_by(email=email).first()
        if existing_user:
            return {"message": "El usuario ya existe"}, 400

        # Crear nuevo usuario
        try:
            new_user = UserModel(
                email=data["email"],
                name=data["name"],
                password=None
            )
            new_user.save_to_db()

            access_token = create_access_token(identity=new_user.json())
            refresh_token = create_refresh_token(identity=new_user.json())

            # Crear la respuesta y establecer las cookies
            response = make_response({
                "message": "User registered successfully.",
                "user": new_user.json(),
            })
            response.set_cookie(
                "access_token", access_token, httponly=True, secure=True, samesite="Strict"
            )
            response.set_cookie(
                "refresh_token", refresh_token, httponly=True, secure=True, samesite="Strict"
            )
            return response

        except Exception as e:
            print(f"Error al guardar usuario: {e}")
            return {"error": "Database error"}, 500
        
class LoginGoogle(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "email", type=str, required=True, help="This field cannot be blank."
    )

    def post(self):
        data = LoginGoogle.parser.parse_args()

        if not data:
            return {"error": "No data provided"}, 400

        email = data["email"]

        # Verifica si el usuario ya existe
        existing_user = UserModel.query.filter_by(
            email=email, active=True
        ).one_or_none()
        if not existing_user:
            return {"message": "El usuario no existe, debe registrarse primero"}, 400
            
        try:

            access_token = create_access_token(identity=existing_user.json())
            refresh_token = create_refresh_token(identity=existing_user.json())

            # Crear la respuesta y establecer las cookies
            response = make_response({
                "message": "User login successfully.",
                "user": existing_user.json(),
            })
            response.set_cookie(
                "access_token", access_token, httponly=True, secure=True, samesite="Strict"
            )
            response.set_cookie(
                "refresh_token", refresh_token, httponly=True, secure=True, samesite="Strict"
            )
            return response

        except Exception as e:
            # Logea la excepción para depurar
            print(f"Error al guardar usuario: {e}")
            return {"error": "Database error"}, 500


class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "name", type=str, required=True, help="This field cannot be blank."
    )
    parser.add_argument(
        "email", type=str, required=True, help="This field cannot be blank."
    )
    parser.add_argument(
        "password", type=str, required=True, help="This field cannot be blank."
    )

    def post(self):
        data = UserRegister.parser.parse_args()

        existing_user = UserModel.query.filter_by(
            email=data["email"], active=True
        ).one_or_none()
        if (
            existing_user is not None
            and existing_user.id != id
            and UserModel.is_valid_email(data["email"])
        ):
            return {"message": "A user with that email already exists"}, 400
        
        if not UserModel.is_valid_email(data["email"]):
            return {"message": "Invalid email format"}, 400

        existing_user = UserModel.query.filter_by(
            email=data["email"], active=False
        ).one_or_none()
        if existing_user is not None:
            user = UserModel.query.filter_by(
                email=data["email"], active=False
            ).one_or_none()
            user.recover_user()
            return user.json(), 201
        
        if data["password"] == "" or len(data["password"]) < 8:
            return {"message": "Password must be at least 8 characters"}, 400

        user = UserModel(**data)
        user.password = generate_password_hash(data["password"], method="pbkdf2")
        try:
            user.save_to_db()
            access_token = create_access_token(identity=user.json())
            refresh_token = create_refresh_token(identity=user.json())
            return {
                "user": user.json(),
                "access_token": access_token,
                "refresh_token": refresh_token,
            }, 200
        except:
            return {"message": "An error occurred creating the user."}, 500


class ManagerRegister(Resource):
    parser = reqparse.RequestParser()
    # User fields
    parser.add_argument(
        "name", type=str, required=True, help="This field cannot be blank."
    )
    parser.add_argument(
        "email", type=str, required=True, help="This field cannot be blank."
    )
    parser.add_argument(
        "password", type=str, required=True, help="This field cannot be blank."
    )
    # Manager specific fields
    parser.add_argument(
        "bankaccount", type=int, required=True, help="Bank account number is required."
    )
    parser.add_argument(
        "accounttype", type=str, required=True, help="Account type is required."
    )
    parser.add_argument(
        "bankentity", type=str, required=True, help="Bank entity is required."
    )

    def post(self):
        data = ManagerRegister.parser.parse_args()

        # Validate email
        existing_user = UserModel.query.filter_by(
            email=data["email"], active=True
        ).one_or_none()
        if (
            existing_user is not None
            and existing_user.id != id
            and UserModel.is_valid_email(data["email"])
        ):
            return {"message": "A user with that email already exists"}, 400
        
        if not UserModel.is_valid_email(data["email"]):
            return {"message": "Invalid email format"}, 400

        # Check for inactive user
        existing_user = UserModel.query.filter_by(
            email=data["email"], active=False
        ).one_or_none()
        if existing_user is not None:
            user = UserModel.query.filter_by(
                email=data["email"], active=False
            ).one_or_none()
            user.recover_user()
            return user.json(), 201

        # Validate password
        if data["password"] == "" or len(data["password"]) < 8:
            return {"message": "Password must be at least 8 characters"}, 400

        try:
            # Create user first
            user_data = {
                "name": data["name"],
                "email": data["email"],
                "password": generate_password_hash(data["password"], method="pbkdf2")
            }
            user = UserModel(**user_data)
            user.save_to_db()

            # Create manager with reference to user
            manager_data = {
                "bankaccount": data["bankaccount"],
                "accounttype": data["accounttype"],
                "bankentity": data["bankentity"],
                "userModel": user
            }
            manager = ManagerModel(**manager_data)
            manager.save_to_db()

            # Generate tokens
            access_token = create_access_token(identity=user.json())
            refresh_token = create_refresh_token(identity=user.json())

            return {
                "user": user.json(),
                "manager": manager.json(),
                "access_token": access_token,
                "refresh_token": refresh_token,
            }, 200
        except Exception as e:
            return {"message": f"An error occurred creating the manager: {str(e)}"}, 500


class UserLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "name", type=str, required=False, help="This field cannot be blank."
    )
    parser.add_argument(
        "email", type=str, required=False, help="This field cannot be blank."
    )
    parser.add_argument(
        "password", type=str, required=True, help="This field cannot be blank."
    )
    # parser.add_argument(
    #     "token", type=str, required=True, help="This field cannot be blank."
    # )

    def post(self):
        data = UserLogin.parser.parse_args()
        email = data["email"]
        name = data["name"]
        password = data["password"]
        # token = data["token"]

        if not email and not name:
            return {"message": "Invalid credentials"}, 401

        user_email = UserModel.query.filter_by(
            email=email, active=True
        ).one_or_none()
        user_name = UserModel.query.filter_by(name=name, active=True).one_or_none()

        if user_email is None and user_name is None:
            return {"message": "Invalid credentials"}, 401

        user = user_email if user_email is not None else user_name
        if not user or not user.check_password(password): #or not user.verify_totp(token):
            return {"message": "Invalid credentials"}, 401

        access_token = create_access_token(identity=user.json())
        refresh_token = create_refresh_token(identity=user.json())
        return {
            "user": user.json(),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, 200


class UserLogout(Resource):
    @jwt_required(verify_type=False)
    def delete(self):
        # Obtener el token actual y sus atributos
        token = get_jwt()
        jti = token["jti"]  # Identificador único del token
        ttype = token["type"]  # Tipo del token (access o refresh)
        exp = token["exp"]  # Timestamp de expiración
        now = int(datetime.now(timezone.utc).timestamp())
        ttl = exp - now  # Tiempo restante hasta la expiración en segundos

        # Bloquear el token en Redis
        try:
            redis_client.setex(jti, ttl, "blocked")  # Almacenar JTI con TTL
            return {"message": "Successfully logged out"}, 200
        except:
            return {"message": "An error occurred logging out"}, 500


class User2FA(Resource):
    @jwt_required(verify_type=False)
    def get(self):
        user = UserModel.find_by_id(get_jwt_identity()["id"])
        if user is None:
            return {"message": "User not found"}, 404

        return {"uri": user.get_totp_uri()}, 200
    
    
class Test(Resource):
    def get(self):
        users = UserModel.get_all_users()

        if users:
            users_json = [user.json() for user in users]
            return users_json, 200
        return {"message": "User not found"}, 404