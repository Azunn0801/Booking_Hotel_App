from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, String
from sqlalchemy.orm import relationship
from app.database import Base # cite: database.py

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)

class Hotel(Base):
    __tablename__ = "hotels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    city = Column(String, index=True)
    city_id = Column(String) # Tham số 'id' (1_318)
    rating = Column(Float) # Điểm đánh giá (guestReview)
    star_rating = Column(Integer) # Tham số 'starRating'
    property_type = Column(String) # Tham số 'propertyType' (34, 131...)
    neighborhood_id = Column(String) # Tham số 'neighborhoods'
    facilities = Column(Text) # Lưu ID tiện nghi dạng chuỗi: "93,80"
    image_url = Column(String)
    review_count = Column(Integer, default=0)
    
    rooms = relationship("Room", back_populates="hotel")

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"))
    room_name = Column(String)
    price = Column(Float) # Lọc theo 'prices'
    amenities = Column(Text) # Tham số 'roomAmenities'
    is_available = Column(Boolean, default=True)

    hotel = relationship("Hotel", back_populates="rooms")

    price = Column(Float, default=0.0)             # Giá bán thực tế (Giá đã giảm)
    original_price = Column(Float, default=0.0)    # Giá gốc (Giá gạch chéo)
    discount_percent = Column(Integer, default=0)  # Phần trăm giảm giá (VD: 10, 15)

class Flight(Base): # Cho endpoint flights/search
    __tablename__ = "flights"
    id = Column(Integer, primary_key=True, index=True)
    airline = Column(String)
    origin = Column(String)
    destination = Column(String)
    departure_time = Column(DateTime)
    price = Column(Float)

class Activity(Base): # Cho endpoint v2/activities/search
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    city = Column(String)
    price = Column(Float)
    rating = Column(Float)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    service_type = Column(String) # 'hotel', 'flight', 'activity'
    service_id = Column(Integer)
    checkin_date = Column(DateTime)
    checkout_date = Column(DateTime)
    total_price = Column(Float)