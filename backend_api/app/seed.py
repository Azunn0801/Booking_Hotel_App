"""
Seed script - Khởi tạo dữ liệu mẫu cho hệ thống
Chạy: python -m app.seed
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models

import hashlib

# Khởi tạo bảng
models.Base.metadata.create_all(bind=engine)

def seed_promotions():
    """Tạo các mã khuyến mãi mẫu"""
    db: Session = SessionLocal()
    
    try:
        # Kiểm tra đã seed chưa
        existing = db.query(models.Promotion).count()
        if existing > 0:
            print(f"Đã có {existing} khuyến mãi. Bỏ qua seed.")
            return

        now = datetime.utcnow()

        promotions = [
            models.Promotion(
                code="SUMMER2026",
                title="Giảm 15% mùa hè",
                description="Áp dụng cho tất cả khách sạn và căn hộ. Giảm 15% trên tổng giá trị đơn hàng.",
                discount_percent=15.0,
                valid_from=now,
                valid_until=now + timedelta(days=90),
                max_usage=500,
                current_usage=0,
                is_active=True,
                image_url="https://img.icons8.com/color/96/sun.png"
            ),
            models.Promotion(
                code="WELCOME10",
                title="Chào mừng thành viên mới",
                description="Giảm 10% cho lần đặt phòng đầu tiên trên Agoda Clone.",
                discount_percent=10.0,
                valid_from=now,
                valid_until=now + timedelta(days=365),
                max_usage=1000,
                current_usage=0,
                is_active=True,
                image_url="https://img.icons8.com/color/96/gift.png"
            ),
            models.Promotion(
                code="VILLA20",
                title="Giảm 20% Villa nghỉ dưỡng",
                description="Áp dụng riêng cho Villa và Entire House. Trải nghiệm nghỉ dưỡng sang trọng với giá ưu đãi.",
                discount_percent=20.0,
                valid_from=now,
                valid_until=now + timedelta(days=60),
                max_usage=200,
                current_usage=0,
                is_active=True,
                image_url="https://img.icons8.com/color/96/beach.png"
            ),
            models.Promotion(
                code="APARTMENT5",
                title="Giảm 5% căn hộ dịch vụ",
                description="Áp dụng cho tất cả căn hộ và serviced apartment.",
                discount_percent=5.0,
                valid_from=now,
                valid_until=now + timedelta(days=120),
                max_usage=300,
                current_usage=0,
                is_active=True,
                image_url="https://img.icons8.com/color/96/apartment.png"
            ),
            models.Promotion(
                code="FLASH25",
                title="Flash Sale - Giảm 25%",
                description="Flash sale giới hạn! Giảm 25% cho tất cả loại hình lưu trú. Nhanh tay kẻo hết!",
                discount_percent=25.0,
                valid_from=now,
                valid_until=now + timedelta(days=7),
                max_usage=50,
                current_usage=0,
                is_active=True,
                image_url="https://img.icons8.com/color/96/lightning-bolt.png"
            ),
            models.Promotion(
                code="LOYALTY12",
                title="Khách hàng thân thiết",
                description="Giảm 12% dành riêng cho khách hàng đã đặt từ 5 lần trở lên.",
                discount_percent=12.0,
                valid_from=now,
                valid_until=now + timedelta(days=180),
                max_usage=100,
                current_usage=0,
                is_active=True,
                image_url="https://img.icons8.com/color/96/star.png"
            ),
        ]

        for promo in promotions:
            db.add(promo)

        db.commit()
        print(f"Đã tạo {len(promotions)} mã khuyến mãi mẫu!")

    except Exception as e:
        db.rollback()
        print(f"Lỗi seed: {e}")
    finally:
        db.close()

def seed_sample_user():
    """Tạo user mẫu để test"""
    db: Session = SessionLocal()

    try:
        hashed_password = hashlib.sha256("123456".encode('utf-8')).hexdigest()
        existing = db.query(models.User).filter(models.User.email == "test@example.com").first()
        if existing:
            existing.hashed_password = hashed_password
            db.commit()
            print("Đã cập nhật mật khẩu user mẫu: test@example.com / 123456 (SHA-256)")
            return

        user = models.User(
            email="test@example.com",
            hashed_password=hashed_password,
            full_name="Nguyen Van Test"
        )
        db.add(user)
        db.commit()
        print("Đã tạo user mẫu: test@example.com / 123456 (SHA-256)")

    except Exception as e:
        db.rollback()
        print(f"Lỗi seed user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("SEEDING DATABASE")
    print("=" * 50)
    seed_promotions()
    seed_sample_user()
    print("=" * 50)
    print("SEED COMPLETE!")
