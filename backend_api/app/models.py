from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    vip_points = Column(Integer, default=0)
    agodacash_balance = Column(Integer, default=0)
    vip_tier = Column(String, default="Bronze")
    vip_progress = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    properties = relationship("Property", back_populates="owner")

class Property(Base):
    __tablename__ = "properties"
    id = Column(String, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    property_type = Column(String) # hotel, apartment, villa
    star_rating = Column(Float, default=3.0)
    city = Column(String, nullable=False)
    address = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    image_url = Column(Text) # Comma-separated image URLs
    status = Column(String, default="Approved") # Draft, Pending, Approved
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="properties")

class Promotion(Base):
    __tablename__ = "promotions"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    discount_percent = Column(Float, nullable=False)
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    max_usage = Column(Integer, default=100)
    current_usage = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    image_url = Column(String)

    bookings = relationship("Booking", back_populates="promotion")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    promotion_id = Column(Integer, ForeignKey("promotions.id"), nullable=True)
    property_id = Column(String)  # RapidAPI property ID
    property_name = Column(String)
    property_type = Column(String)  # hotel, apartment, villa
    property_image = Column(String)
    checkin_date = Column(String)
    checkin_time = Column(String, nullable=True)
    checkout_date = Column(String)
    total_price = Column(Float)
    original_price = Column(Float)
    discount_amount = Column(Float, default=0)
    status = Column(String, default="confirmed")  # confirmed, cancelled, completed
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    promotion = relationship("Promotion", back_populates="bookings")

class UserPromotion(Base):
    __tablename__ = "user_promotions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    promotion_id = Column(Integer, ForeignKey("promotions.id"))
    claimed_at = Column(DateTime, default=datetime.utcnow)
    comment = Column(Text)
    date = Column(String)
    checkin_date = Column(String)

class Place(Base):
    __tablename__ = "places"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    type_id = Column(Integer)
    type_name = Column(String)
    sub_type_id = Column(Integer)
    sub_type_name = Column(String)
    city_id = Column(Integer)
    city_name = Column(String)
    country_id = Column(Integer)
    country_name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    search_type = Column(Integer)
    active_hotels = Column(Integer)
    state_id = Column(Integer)
    state_name = Column(String)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    property_name = Column(String)
    rating = Column(Float)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

class InboxMessage(Base):
    __tablename__ = "inbox_messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    sender_name = Column(String)
    subject = Column(String)
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
