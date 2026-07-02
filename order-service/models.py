from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Order(db.Model):

    __tablename__ = "orders"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        nullable=False
    )

    product_name = db.Column(
        db.String(255),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )