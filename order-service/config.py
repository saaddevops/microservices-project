import os

class Config:

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://"
        f"{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}"
        f"@postgres:5432/"
        f"{os.getenv('ORDER_DB')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv(
        "SECRET_KEY"
    )

    REDIS_HOST = os.getenv(
        "REDIS_HOST"
    )