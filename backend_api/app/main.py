from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, database
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import text

# Khởi tạo database dựa trên model đầy đủ (User, Hotel, Room, Flight, Activity, Booking)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Agoda Full Service API Clone")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Đoạn code này đảm bảo View luôn tồn tại trong SQLite
def ensure_view_exists(db):
    view_sql = """
    -- Đảm bảo câu lệnh SQL trong View lấy đúng cột:
    CREATE VIEW IF NOT EXISTS vw_Hotel_API_List AS
    SELECT 
        h.id, h.name, h.address, h.city, h.city_id, h.star_rating, 
        h.rating as score, 
        h.review_count,  -- Lấy thẳng từ bảng hotels, KHÔNG ĐỂ SỐ CỨNG Ở ĐÂY
        h.image_url, h.latitude, h.longitude,
        (SELECT MIN(price) FROM rooms WHERE rooms.hotel_id = h.id) as price,
        1 as is_available,
        1 as is_preferred
    FROM hotels h;
    """
    db.execute(text(view_sql))
    db.commit()

# --- 1. HOTELS SERVICE (Khớp với image_e6fc62.png) ---

# --- 1. HOTELS SERVICE (Khớp với image_e6fc62.png) ---

@app.get("/hotels/auto-complete")
def hotels_auto_complete(q: str = Query(...), db: Session = Depends(get_db)):
    # Tìm kiếm gợi ý thành phố/vùng
    return db.query(models.Hotel.city).filter(models.Hotel.city.contains(q)).distinct().all()

@app.get("/hotels/search-overnight")
def search_overnight(
    db: Session = Depends(get_db),
    id: str = Query(..., description="Mã vùng bắt buộc"),
    starRating: Optional[str] = None,
    prices: Optional[str] = None,
    sort: str = "Ranking,Desc",
    limit: int = 10
):
    query = db.query(models.Hotel).filter(models.Hotel.city_id == id)
    
    # Logic lọc sao và giá giữ nguyên...
    
    hotels = query.distinct().limit(limit).all()
    
    # --- PHẦN XỬ LÝ ĐỂ LẤY GIÁ GỐC VÀ KHUYẾN MÃI ---
    results = []
    for h in hotels:
        # 1. Tìm thông tin PHÒNG RẺ NHẤT của khách sạn này (Lấy toàn bộ object Room)
        min_room = db.query(models.Room).filter(models.Room.hotel_id == h.id).order_by(models.Room.price.asc()).first()
        
        # Bóc tách 3 loại giá từ bảng Room (nếu không có phòng thì mặc định là 0)
        price = min_room.price if min_room else 0
        original_price = min_room.original_price if min_room else 0
        discount_percent = min_room.discount_percent if min_room else 0
        
        hotel_data = {
            "id": str(h.id),
            "name": h.name,
            "address": h.address,
            "city": h.city,
            "city_id": h.city_id,
            "star_rating": h.star_rating,
            "image_url": h.image_url,
            "is_available": True,
            
            # --- 3 TRƯỜNG GIÁ TRỊ MỚI ĐỂ HIỂN THỊ UI ---
            "price": price,                       # Giá bán thực tế
            "original_price": original_price,     # Giá gạch chéo
            "discount_percent": discount_percent, # Cột % giảm giá
            
            "score": h.rating or 0.0,    
            "review_count": h.review_count or 0,  # Đã lấy số thật từ DB
            "is_preferred": True,
            "latitude": h.latitude if hasattr(h, 'latitude') else 0.0,
            "longitude": h.longitude if hasattr(h, 'longitude') else 0.0
        }
        results.append(hotel_data)

    return results

@app.get("/hotels/details")
def get_hotel_details(hotel_id: int, db: Session = Depends(get_db)):
    hotel = db.query(models.Hotel).filter(models.Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách sạn")
    return hotel

@app.get("/hotels/room-prices")
def get_room_prices(hotel_id: int, db: Session = Depends(get_db)):
    return db.query(models.Room).filter(models.Room.hotel_id == hotel_id).all()

# --- 2. FLIGHTS SERVICE (Khớp với image_e6fc20.png) ---

@app.get("/flights/search-one-way")
def search_flights(origin: str, destination: str, db: Session = Depends(get_db)):
    return db.query(models.Flight).filter(
        models.Flight.origin == origin, 
        models.Flight.destination == destination
    ).all()

# --- 3. ACTIVITIES SERVICE (Khớp với image_e6fc3f.png) ---

@app.get("/v2/activities/search")
def search_activities(city: str, db: Session = Depends(get_db)):
    return db.query(models.Activity).filter(models.Activity.city == city).all()

# --- 4. UTILITIES (Khớp với image_e6fc5c.png) ---

@app.get("/languages")
def get_languages():
    return [{"name": "Tiếng Việt", "code": "vi-vn"}, {"name": "English", "code": "en-us"}]

@app.get("/currencies")
def get_currencies():
    return [{"name": "Việt Nam Đồng", "code": "VND"}, {"name": "US Dollar", "code": "USD"}]

    # --- 5. AUTH SERVICE (Đăng ký/Đăng nhập) ---

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

@app.post("/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email đã tồn tại")
    new_user = models.User(
        email=user.email, 
        hashed_password=user.password, # Trong thực tế cần băm mật khẩu
        full_name=user.full_name
    )
    db.add(new_user)
    db.commit()
    return {"message": "Đăng ký thành công"}

@app.post("/auth/login")
def login(email: str = Query(...), password: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email, models.User.hashed_password == password).first()
    if not user:
        raise HTTPException(status_code=401, detail="Sai tài khoản hoặc mật khẩu")
    return {"message": "Đăng nhập thành công", "user_id": user.id, "full_name": user.full_name}

# --- 6. BOOKING SERVICE (Đặt chỗ) ---

class BookingCreate(BaseModel):
    user_id: int
    service_type: str # 'hotel', 'flight', 'activity'
    service_id: int
    checkin_date: str
    checkout_date: str
    total_price: float

@app.post("/bookings")
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    new_booking = models.Booking(
        user_id=booking.user_id,
        service_type=booking.service_type,
        service_id=booking.service_id,
        checkin_date=datetime.strptime(booking.checkin_date, "%Y-%m-%d"),
        checkout_date=datetime.strptime(booking.checkout_date, "%Y-%m-%d"),
        total_price=booking.total_price
    )
    db.add(new_booking)
    db.commit()
    return {"status": "success", "message": "Đặt chỗ thành công!"}