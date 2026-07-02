from flask import Flask, request

from flask_cors import CORS

from config import Config
from models import db, Order

from sqlalchemy.exc import OperationalError

from functools import wraps

import jwt
import time
import redis
import json
import pika

app = Flask(__name__)

# Enable CORS
CORS(app)

# Load configuration
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Redis connection
redis_client = redis.Redis(
    host=app.config["REDIS_HOST"],
    port=6379,
    decode_responses=True
)

# Wait for PostgreSQL to be ready
for attempt in range(10):

    try:

        with app.app_context():
            db.create_all()

        print(
            "Orders database connected successfully"
        )

        break

    except OperationalError:

        print(
            f"Database not ready. Retry {attempt + 1}/10"
        )

        time.sleep(3)


# JWT Authentication Decorator
def token_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        auth_header = request.headers.get(
            "Authorization"
        )

        if auth_header:

            parts = auth_header.split(" ")

            if len(parts) == 2:

                token = parts[1]

        if not token:

            return {
                "message": "Token is missing"
            }, 401

        try:

            data = jwt.decode(
                token,
                app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

            current_user_id = data[
                "user_id"
            ]

            current_user_email = data[
                "email"
            ]

        except Exception:

            return {
                "message": "Invalid token"
            }, 401

        return f(
            current_user_id,
            current_user_email,
            *args,
            **kwargs
        )

    return decorated


@app.route("/")
def home():

    return {
        "message": "Order Service Running"
    }


@app.route(
    "/orders",
    methods=["POST"]
)
@token_required
def create_order(
    current_user_id,
    current_user_email
):

    data = request.get_json()

    product_name = data.get(
        "product_name"
    )

    quantity = data.get(
        "quantity"
    )

    if not product_name:

        return {
            "message":
            "Product name required"
        }, 400

    if not quantity:

        return {
            "message":
            "Quantity required"
        }, 400

    order = Order(

        user_id=current_user_id,

        product_name=product_name,

        quantity=quantity
    )

    db.session.add(order)

    db.session.commit()

    message = {

        "user_id": current_user_id,

        "email": current_user_email,

        "product_name": product_name,

        "quantity": quantity
    }

    try:

        rabbitmq_connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host="rabbitmq"
            )
        )

        rabbitmq_channel = (
            rabbitmq_connection.channel()
        )

        rabbitmq_channel.queue_declare(
            queue="order_created"
        )

        rabbitmq_channel.basic_publish(

            exchange="",

            routing_key="order_created",

            body=json.dumps(message)
        )

        rabbitmq_connection.close()

        print(
            f"Published order event: {message}"
        )

    except Exception as e:

        print(
            f"RabbitMQ Error: {e}"
        )

    redis_client.delete(
        f"orders:{current_user_id}"
    )

    print(
        f"Cache cleared for user {current_user_id}"
    )

    return {
        "message":
        "Order created successfully"
    }, 201


@app.route(
    "/orders",
    methods=["GET"]
)
@token_required
def get_orders(
    current_user_id,
    current_user_email
):

    cache_key = (
        f"orders:{current_user_id}"
    )

    cached_orders = (
        redis_client.get(cache_key)
    )

    if cached_orders:

        print(
            "Serving from Redis cache"
        )

        return json.loads(
            cached_orders
        )

    print(
        "Serving from PostgreSQL"
    )

    orders = Order.query.filter_by(
        user_id=current_user_id
    ).all()

    result = []

    for order in orders:

        result.append({

            "id": order.id,

            "product_name":
            order.product_name,

            "quantity":
            order.quantity
        })

    redis_client.set(
        cache_key,
        json.dumps(result),
        ex=60
    )

    return result


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5001
    )