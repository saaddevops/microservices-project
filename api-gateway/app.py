from flask import Flask, request, jsonify

from flask_cors import CORS

import requests

app = Flask(__name__)

CORS(app)

USER_SERVICE = "http://user-service:5000"
ORDER_SERVICE = "http://order-service:5001"


@app.route("/")
def home():

    return {
        "message": "API Gateway Running"
    }


# Register
@app.route(
    "/register",
    methods=["POST"]
)
def register():

    response = requests.post(
        f"{USER_SERVICE}/register",
        json=request.json
    )

    return (
        response.json(),
        response.status_code
    )


# Login
@app.route(
    "/login",
    methods=["POST"]
)
def login():

    response = requests.post(
        f"{USER_SERVICE}/login",
        json=request.json
    )

    return (
        response.json(),
        response.status_code
    )


# Create Order
@app.route(
    "/orders",
    methods=["POST"]
)
def create_order():

    response = requests.post(

        f"{ORDER_SERVICE}/orders",

        json=request.json,

        headers={
            "Authorization":
            request.headers.get(
                "Authorization"
            )
        }
    )

    return (
        response.json(),
        response.status_code
    )


# Get Orders
@app.route(
    "/orders",
    methods=["GET"]
)
def get_orders():

    response = requests.get(

        f"{ORDER_SERVICE}/orders",

        headers={
            "Authorization":
            request.headers.get(
                "Authorization"
            )
        }
    )

    return (
        response.json(),
        response.status_code
    )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8000
    )