import pika
import json
import time
import os
import smtplib

from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv(
    "EMAIL_ADDRESS"
)

EMAIL_PASSWORD = os.getenv(
    "EMAIL_PASSWORD"
)

print(
    "Notification Service Starting...",
    flush=True
)

while True:

    try:

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host="rabbitmq"
            )
        )

        print(
            "Connected to RabbitMQ",
            flush=True
        )

        break

    except Exception as e:

        print(
            f"Waiting for RabbitMQ... {e}",
            flush=True
        )

        time.sleep(5)

channel = connection.channel()

channel.queue_declare(
    queue="order_created"
)

print(
    "Notification Service Started",
    flush=True
)


def send_email(order):

    try:

        msg = EmailMessage()

        msg["Subject"] = (
            "Order Created Successfully"
        )

        msg["From"] = EMAIL_ADDRESS

        msg["To"] = order["email"]

        msg.set_content(
            f"""
Hello,

Your order has been created successfully.

Product: {order['product_name']}
Quantity: {order['quantity']}

Thank you.
"""
        )

        with smtplib.SMTP(
            "smtp.gmail.com",
            587
        ) as smtp:

            smtp.starttls()

            smtp.login(
                EMAIL_ADDRESS,
                EMAIL_PASSWORD
            )

            smtp.send_message(msg)

        print(
            f"Email Sent To {order['email']}",
            flush=True
        )

    except Exception as e:

        print(
            f"Email Error: {e}",
            flush=True
        )


def callback(
    ch,
    method,
    properties,
    body
):

    order = json.loads(
        body
    )

    print(
        f"Order Received: {order}",
        flush=True
    )

    if "email" in order:

        send_email(order)


channel.basic_consume(
    queue="order_created",
    on_message_callback=callback,
    auto_ack=True
)

print(
    "Waiting for messages...",
    flush=True
)

channel.start_consuming()