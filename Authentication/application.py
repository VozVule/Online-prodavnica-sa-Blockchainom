from flask import Flask, request, Response, jsonify, json
from configuration import Configuration
from models import *
from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import and_
import re

application = Flask(__name__)
application.config.from_object(Configuration)


@application.route("/register_customer", methods=["POST"])
def register_customer():
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    fname_empty = len(forename) == 0
    sname_empty = len(surname) == 0
    email_empty = len(email) == 0
    password_empty = len(password) == 0

    if fname_empty:
        data = {
            "message": "Field forename is missing."
        }
        return Response(json.dumps(data), status = 400)
    if sname_empty:
        data = {
            "message": "Field surname is missing."
        }
        return Response(json.dumps(data), status = 400)
    if email_empty:
        data = {
            "message": "Field email is missing."
        }
        return Response(json.dumps(data), status = 400)
    if password_empty:
        data = {
            "message": "Field password is missing."
        }
        return Response(json.dumps(data), status = 400)

    email_regex = r'^\S+@\S+\.[A-Za-z]{2,}$'
    if not re.match(email_regex, email):
        data = {
            "message": "Invalid email."
        }
        return Response(json.dumps(data), status = 400)

    if len(password) < 8:
        data = {
            "message": "Invalid password."
        }
        return Response(json.dumps(data), status = 400)

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return Response(json.dumps({"message": "Email already exists."}), status=400)

    user = User(forename = forename, surname = surname, email=email, password = password)
    database.session.add(user)
    database.session.commit()

    user_role = UserRole(userId = user.id, roleId = 3)
    database.session.add(user_role)
    database.session.commit()

    return Response(status=200)


@application.route("/register_courier", methods=["POST"])
def register_courier():
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    fname_empty = len(forename) == 0
    sname_empty = len(surname) == 0
    email_empty = len(email) == 0
    password_empty = len(password) == 0

    if fname_empty:
        data = {
            "message": "Field forename is missing."
        }
        return Response(json.dumps(data), status = 400)
    if sname_empty:
        data = {
            "message": "Field surname is missing."
        }
        return Response(json.dumps(data), status = 400)
    if email_empty:
        data = {
            "message": "Field email is missing."
        }
        return Response(json.dumps(data), status = 400)
    if password_empty:
        data = {
            "message": "Field password is missing."
        }
        return Response(json.dumps(data), status = 400)

    email_regex = r'^\S+@\S+\.[A-Za-z]{2,}$'
    if not re.match(email_regex, email):
        data = {
            "message": "Invalid email."
        }
        return Response(json.dumps(data), status = 400)

    if len(password) < 8:
        data = {
            "message": "Invalid password."
        }
        return Response(json.dumps(data), status = 400)

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return Response(json.dumps({"message": "Email already exists."}), status=400)

    user = User(forename = forename, surname = surname, email=email, password = password)
    database.session.add(user)
    database.session.commit()

    user_role = UserRole(userId = user.id, roleId = 2)
    database.session.add(user_role)
    database.session.commit()

    return Response(status=200)


jwt = JWTManager(application)


@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    email_empty = len(email) == 0
    password_empty = len(password) == 0

    if email_empty:
        return Response(json.dumps({"message": "Field email is missing."}), status=400)
    if password_empty:
        return Response(json.dumps({"message": "Field password is missing."}), status=400)

    email_regex = r'^\S+@\S+\.[A-Za-z]{2,}$'
    if not re.match(email_regex, email):
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    user = User.query.filter(and_(User.email == email, User.password == password)).first()
    if not user:
        return Response(json.dumps({"message": "Invalid credentials."}), status=400)

    additional_claims = {
        "forename"  : user.forename,
        "surname"   : user.surname,
        "password"  : user.password,
        "roles"     : [str(role) for role in user.roles],
    }

    access_token = create_access_token(
        identity=user.email,
        additional_claims= additional_claims,
        expires_delta=Configuration.JWT_ACCESS_TOKEN_EXPIRES
    )

    return Response(json.dumps({"accessToken": access_token}), status=200)


@application.route("/delete", methods=["POST"])
@jwt_required()
def delete():
    user_email = get_jwt_identity()
    print(f"ovde sam?! yessir {user_email}")
    user = User.query.filter_by(email = user_email).first()
    if not user:
        return Response(json.dumps({"message": "Unknown user."}), status = 400)
    UserRole.query.filter_by(userId = user.id).delete()
    User.query.filter_by(email = user.email).delete()
    database.session.commit()

    return Response(status=200)


@application.route("/", methods=["GET"])
def index():
    return "Hello world!"


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0")