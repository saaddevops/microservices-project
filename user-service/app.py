from flask import Flask, request

from flask_cors import CORS

from config import Config
from models import db, User

from sqlalchemy.exc import OperationalError

import jwt
import datetime
import time

app = Flask(__name__)

# Enable CORS
CORS(app)

app.config.from_object(Config)

db.init_app(app)

# Wait for PostgreSQL to be ready
for attempt in range(10):

    try:

        with app.app_context():
            db.create_all()

        print("Database connected successfully")

        break

    except OperationalError:

        print(
            f"Database not ready. Retry {attempt + 1}/10"
        )

        time.sleep(3)


@app.route("/")
def home():

    return {
        "message": "User Service Running"
    }


@app.route(
    "/register",
    methods=["POST"]
)
def register():

    data = request.get_json()

    existing_user = User.query.filter_by(
        email=data["email"]
    ).first()

    if existing_user:

        return {
            "message": "Email already exists"
        }, 400

    user = User(

        username=data["username"],

        email=data["email"],

        password=data["password"]
    )

    db.session.add(user)

    db.session.commit()

    return {
        "message": "User registered successfully"
    }, 201


@app.route(
    "/login",
    methods=["POST"]
)
def login():

    data = request.get_json()

    user = User.query.filter_by(
        email=data["email"]
    ).first()

    if not user:

        return {
            "message": "Invalid email or password"
        }, 401

    if user.password != data["password"]:

        return {
            "message": "Invalid email or password"
        }, 401

    token = jwt.encode(

        {

            "user_id": user.id,

            "email": user.email,

            "exp": datetime.datetime.utcnow()
            + datetime.timedelta(hours=1)

        },

        app.config["SECRET_KEY"],

        algorithm="HS256"
    )

    return {
        "token": token
    }


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )