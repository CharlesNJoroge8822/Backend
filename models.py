from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db


class User(db.Model):
    __tablename__ = 'users'  

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="Client")  # Roles: Admin, Client
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    image = db.Column(db.String(200), nullable=True, default="default.jpg")  # Profile picture URL

    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)
    agreements = db.relationship('Agreement', backref='user', lazy=True)


class Space(db.Model):
    __tablename__ = 'spaces'  

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False, index=True)
    price_per_hour = db.Column(db.Float, nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    availability = db.Column(db.String(500), nullable=False)  # JSON String of availability slots
    images = db.Column(db.String(500), nullable=True)  # Comma-separated image URLs

    # Relationships
    bookings = db.relationship('Booking', backref='space', lazy=True)  # Multiple bookings allowed


class Booking(db.Model):
    __tablename__ = 'bookings'  

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="Pending")  # Pending, Confirmed, Cancelled

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey('spaces.id'), nullable=False)  # Allows multiple bookings over time

    # Relationship
    payment = db.relationship('Payment', backref='booking', uselist=False)

    # Ensure no overlapping bookings
    @staticmethod
    def is_space_available(space_id, start_time, end_time):
        existing_booking = Booking.query.filter(
            Booking.space_id == space_id,
            Booking.status == "Confirmed",  # Only check for confirmed bookings
            Booking.end_time > start_time  # Ensuring no overlap
        ).first()
        return existing_booking is None


class Payment(db.Model):
    __tablename__ = 'payments'  

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="Processing")  # Processing, Completed, Failed
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign Keys
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Mpesa-specific fields
    mpesa_transaction_id = db.Column(db.String(100), unique=True, nullable=False, index=True)  # Mpesa transaction reference
    phone_number = db.Column(db.String(20), nullable=False)  # Phone number used for payment

    def __init__(self, booking_id, user_id, amount, mpesa_transaction_id, phone_number):
        self.booking_id = booking_id
        self.user_id = user_id
        self.amount = amount
        self.mpesa_transaction_id = mpesa_transaction_id
        self.phone_number = phone_number


class Agreement(db.Model):
    __tablename__ = 'agreements'  

    id = db.Column(db.Integer, primary_key=True)
    terms = db.Column(db.Text, nullable=False)
    accepted = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey('spaces.id'), nullable=False)
