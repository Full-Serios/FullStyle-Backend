from models.user_model import UserModel
from models.manager_model import ManagerModel
from datetime import datetime, timezone
from flask_restful import Resource, reqparse
import utils.encryption as encryption
import utils.send_email as send_email
import bcrypt
from werkzeug.security import generate_password_hash
from models.token_blocklist_model import redis_client
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    create_refresh_token,
    get_jwt,
    decode_token
)
from flask import make_response
from config.db_config import db
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from datetime import timedelta

class User(Resource):
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
            if ("google" in user.auth_provider):
                user.auth_provider = "credentials-google"
        try:
            user.save_to_db()
            return user.json(), 200
        except:
            return {"message": "An error occurred updating the user."}, 500

    @jwt_required()
    def delete(self, id):
        user = UserModel.find_by_id(id)
        if user:
            user.delete_from_db()
            return {"message": "User deleted"}, 200
        # Obtener información del token actual
        token = get_jwt()
        jti = token["jti"]  # Identificador único del token
        exp = token["exp"]  # Timestamp de expiración
        now = int(datetime.now(timezone.utc).timestamp())
        ttl = exp - now  # Tiempo restante hasta la expiración en segundos

        return {"message": "User deleted"}, 200
        # Bloquear el token en Redis con el TTL
        # try:
        #     redis_client.setex(jti, ttl, "blocked")  # Almacenar JTI con TTL
        #     return {"message": "User deleted and token invalidated"}, 200
        # except:
        #     return {"message": "An error occurred deleting the user."}, 500

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

            access_token = create_access_token(identity=str(new_user.id))
            refresh_token = create_refresh_token(identity=str(new_user.id))

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
    parser.add_argument(
        "token", type=str, required=True, help="Google token is required."
    )

    def post(self):
        data = LoginGoogle.parser.parse_args()

        if not data:
            return {"error": "No data provided"}, 400

        email = data["email"]
        token = data["token"]

        try:
            # Verificar el token de Google
            GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")

            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                GOOGLE_CLIENT_ID
            )

            # Verificar que el email del token coincide con el proporcionado
            if idinfo['email'] != email:
                return {"error": "Email verification failed"}, 401

            # Verifica si el usuario ya existe
            existing_user = UserModel.query.filter_by(
                email=email, active=True
            ).one_or_none()

            if not existing_user:
                new_user = UserModel(
                    email=idinfo["email"],
                    name=idinfo["name"],
                    password=None,
                    auth_provider="google",
                    google_id=idinfo["sub"]
                )
                new_user.save_to_db()

                access_token = create_access_token(identity=str(new_user.id))
                refresh_token = create_refresh_token(identity=str(new_user.id))

                response = make_response({
                    "message": "User created and logged in successfully.",
                    "user": new_user.json(),
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                })
                return response

            if existing_user.password and existing_user.auth_provider == "credentials":
                # save google id to user
                existing_user.google_id = idinfo["sub"]
                existing_user.auth_provider += "-google"
                existing_user.save_to_db()

            is_manager_role = UserModel.is_manager(existing_user.id)

            # Crear tokens JWT
            access_token = create_access_token(identity=str(existing_user.id))
            refresh_token = create_refresh_token(identity=str(existing_user.id))

            # Crear la respuesta y establecer las cookies
            response = make_response({
                "message": "User login successfully.",
                "user": existing_user.json(),
                "access_token": access_token,
                "refresh_token": refresh_token,
                "manager": is_manager_role
            })
            return response

        except ValueError:
            # Token inválido
            print(f"Invalid token: {token}")


            return {"error": "Invalid token"}, 401
        except Exception as e:
            # Logea la excepción para depurar
            print(f"Error during login: {e}")
            return {"error": "Authentication error", "e": e}, 500



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
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
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
            # Crear savepoint
            with db.session.begin_nested():
                # Create user first
                user_data = {
                    "name": data["name"],
                    "email": data["email"],
                    "password": generate_password_hash(data["password"], method="pbkdf2")
                }
                user = UserModel(**user_data)
                db.session.add(user)

                # Hacer flush para obtener el ID del usuario
                db.session.flush()

                # Create manager with reference to user
                manager_data = {
                    "bankaccount": data["bankaccount"],
                    "accounttype": data["accounttype"],
                    "bankentity": data["bankentity"],
                    "userModel": user
                }
                manager = ManagerModel(**manager_data)
                db.session.add(manager)

            # Commit de la sesión principal
            db.session.commit()

            # Generate tokens
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))

            return {
                "user": user.json(),
                "manager": manager.json(),
                "access_token": access_token,
                "refresh_token": refresh_token,
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"message": f"Ocurrio un error registrando el gerente: {str(e)}"}, 500


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

    def post(self):
        data = UserLogin.parser.parse_args()
        email = data["email"]
        name = data["name"]
        password = data["password"]

        if not email and not name:
            return {"message": "Invalid credentials"}, 401

        user_email = UserModel.query.filter_by(
            email=email, active=True
        ).one_or_none()
        user_name = UserModel.query.filter_by(name=name, active=True).one_or_none()

        if user_email is None and user_name is None:
            return {"message": "Invalid credentials"}, 401

        user = user_email if user_email is not None else user_name
        if not user or not user.check_password(password):
            return {"message": "Invalid credentials"}, 401

        # Usar el método is_manager que implementamos
        is_manager_role = UserModel.is_manager(user.id)

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return {
            "user": user.json(),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "manager": is_manager_role,
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

class ResetPasswordRequest(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("email", type=str, required=True, help="This field cannot be blank.")

    def post(self):
        try:
            data = ResetPasswordRequest.parser.parse_args()
            email = data["email"]

            user = UserModel.query.filter_by(email=email, active=True).first()
            if not user:
                return {"message": "User not found"}, 404

            reset_token = create_access_token(identity=str(user.id), expires_delta=timedelta(minutes=15))

            res = send_email.ResetPassword(email, user.name, reset_token)

            return {"message": "A reset link has been sent to your email"}, 200
        except Exception as e:
            return {"message": f"Error: {str(e)}"}, 400

class ResetPasswordConfirm(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("token", type=str, required=True, help="Token is required.")
    parser.add_argument("password", type=str, required=True, help="New password is required.")

    def post(self):
        data = ResetPasswordConfirm.parser.parse_args()
        token = data["token"]
        new_password = data["password"]

        if len(new_password) < 8:
            return {"message": "Password must be at least 8 characters"}, 400

        try:
            decoded_token = decode_token(token)
            print(decoded_token)
            user_id = decoded_token.get("sub")

            user = UserModel.find_by_id(user_id)
            if not user:
                return {"message": "Invalid token or user not found"}, 400

            # Actualizar la contraseña
            user.password = generate_password_hash(new_password, method="pbkdf2")
            if ("google" in user.auth_provider):
                user.auth_provider = "credentials-google"
            user.save_to_db()

            return {"message": "Password successfully reset"}, 200

        except Exception as e:
            return {"message": f"Error: {str(e)}"}, 400
