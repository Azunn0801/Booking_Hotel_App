import requests
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine #
from app import models
import json

# Khởi tạo toàn bộ các bảng mới (User, Hotel, Room, Flight, Activity, Booking)
models.Base.metadata.create_all(bind=engine) #

def fetch_and_seed_final():
    url = "https://agoda-com.p.rapidapi.com/hotels/search-overnight"
    querystring = {
        "id": "1_318",
        "checkinDate": "2026-06-05",
        "checkoutDate": "2026-06-07",
        "limit": "20",
        "language":"vi-vn",
        "currency":"VND"
    }
    headers = {
        "x-rapidapi-key": "7ac8e7f4aamshe3afd8116a3789dp118aa9jsnf974be0679d4",
        "x-rapidapi-host": "agoda-com.p.rapidapi.com"
    }

    print("📡 Đang nạp dữ liệu vào cấu trúc Model hoàn chỉnh...")
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json().get('data', {}).get('citySearch', {}).get('properties', [])

        db: Session = SessionLocal()
        count_h = 0
        count_r = 0

        for item in data:
            content = item.get('content') or {}
            info = content.get('informationSummary') or {}
            
            hotel_name = info.get('localeName') or info.get('defaultName')
            if not hotel_name: continue

            # --- TRÍCH XUẤT REVIEW CHUẨN XÁC TỪ JSON ---
            reviews_data = content.get('reviews') or {}
            cumulative = reviews_data.get('cumulative') or {}
            real_score = cumulative.get('score') or 0.0
            real_review_count = cumulative.get('reviewCount') or 0 

            # 1. Lưu mới hoặc CẬP NHẬT Khách sạn
            hotel = db.query(models.Hotel).filter(models.Hotel.name == hotel_name).first()
            
            if not hotel:
                # Xử lý link ảnh
                img_url = ""
                hotel_images = content.get('images', {}).get('hotelImages') or []
                if hotel_images:
                    urls = hotel_images[0].get('urls') or []
                    if urls: img_url = urls[0].get('value', '')
                if img_url.startswith('//'): img_url = f"https:{img_url}"

                hotel = models.Hotel(
                    name=hotel_name,
                    address=f"{info.get('address', {}).get('area', {}).get('name', '')}, {info.get('address', {}).get('city', {}).get('name', '')}",
                    city=info.get('address', {}).get('city', {}).get('name', 'New York'),
                    city_id="1_318",
                    rating=float(real_score),              # Điểm thật
                    review_count=int(real_review_count),     # Số lượng thật
                    star_rating=int(info.get('rating') or 0),
                    property_type=info.get('propertyType', 'Hotel'),
                    image_url=img_url
                )
                db.add(hotel)
                db.flush() 
                count_h += 1
            else:
                # --- QUAN TRỌNG: NẾU KHÁCH SẠN ĐÃ CÓ, PHẢI UPDATE LẠI REVIEW ---
                hotel.rating = float(real_score)
                hotel.review_count = int(real_review_count)

            # 2. Xử lý Phòng (Giữ nguyên logic của bạn)
            pricing = item.get('pricing') or {}
            offers = pricing.get('offers') or []
            if offers:
                room_data = offers[0].get('roomOffers', [{}])[0].get('room', {})
                price_val = 0
                price_list = room_data.get('pricing') or []
                if price_list:
                    price_val = price_list[0].get('price', {}).get('perNight', {}).get('inclusive', {}).get('display', 0)

                new_room = models.Room(
                    hotel_id=hotel.id,
                    room_name=item.get('enrichment', {}).get('roomInformation', {}).get('cheapestRoomName', 'Standard Room'),
                    price=float(price_val),
                    is_available=pricing.get('isAvailable', True)
                )
                db.add(new_room)
                count_r += 1

        db.commit()
        db.close()
        print(f"✅ Thành công! Đã nạp {count_h} khách sạn và {count_r} phòng vào database.")

    except Exception as e:
        print(f"❌ Lỗi nạp dữ liệu: {e}")

if __name__ == "__main__":
    fetch_and_seed_final()