-- ==============================================================================
-- CƠ SỞ DỮ LIỆU ĐẶT PHÒNG ĐA LOẠI HÌNH (HOTEL, VILLA, APARTMENT)
-- BẢN CẬP NHẬT TỐI ƯU CHO APP ANDROID & FASTAPI
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS agoda_universal_db;
USE agoda_universal_db;

-- ------------------------------------------------------------------------------
-- 1. QUẢN LÝ NGƯỜI DÙNG
-- ------------------------------------------------------------------------------
CREATE TABLE Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    loyalty_points INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 2. QUẢN LÝ THỰC THỂ LƯU TRÚ (PROPERTIES) & TIỆN ÍCH
-- ------------------------------------------------------------------------------

CREATE TABLE Amenities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    icon_url VARCHAR(255),
    amenity_scope ENUM('property_level', 'unit_level') NOT NULL 
);

-- [ĐÃ CẬP NHẬT]: Thêm city_id và is_preferred
CREATE TABLE Properties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    agoda_id VARCHAR(50) UNIQUE,
    property_type ENUM('hotel', 'villa', 'apartment', 'homestay', 'resort') NOT NULL,
    name VARCHAR(255) NOT NULL,
    star_rating DECIMAL(2,1) NULL, 
    description TEXT,
    address VARCHAR(255),
    city VARCHAR(100),
    city_id VARCHAR(50), -- BỔ SUNG: Mã thành phố để App Search (VD: "1_318")
    country VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    check_in_time TIME,
    check_out_time TIME,
    is_preferred BOOLEAN DEFAULT FALSE, -- BỔ SUNG: Cờ đánh dấu Khách sạn nổi bật
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Property_Amenities (
    property_id INT,
    amenity_id INT,
    PRIMARY KEY (property_id, amenity_id),
    FOREIGN KEY (property_id) REFERENCES Properties(id) ON DELETE CASCADE,
    FOREIGN KEY (amenity_id) REFERENCES Amenities(id) ON DELETE CASCADE
);

CREATE TABLE Property_Images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (property_id) REFERENCES Properties(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------------------------
-- 3. QUẢN LÝ ĐƠN VỊ LƯU TRÚ (UNITS - CÁC PHÒNG)
-- ------------------------------------------------------------------------------

CREATE TABLE Unit_Types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT NOT NULL,
    unit_category ENUM('room', 'apartment', 'entire_place', 'bed_in_dorm') NOT NULL,
    name VARCHAR(150) NOT NULL, 
    description TEXT,
    max_guests INT NOT NULL DEFAULT 2,
    number_of_bedrooms INT DEFAULT 1,
    number_of_bathrooms INT DEFAULT 1,
    area_sqm DECIMAL(6,2),
    FOREIGN KEY (property_id) REFERENCES Properties(id) ON DELETE CASCADE
);

CREATE TABLE Unit_Amenities (
    unit_type_id INT,
    amenity_id INT,
    PRIMARY KEY (unit_type_id, amenity_id),
    FOREIGN KEY (unit_type_id) REFERENCES Unit_Types(id) ON DELETE CASCADE,
    FOREIGN KEY (amenity_id) REFERENCES Amenities(id) ON DELETE CASCADE
);

CREATE TABLE Unit_Images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    unit_type_id INT NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    FOREIGN KEY (unit_type_id) REFERENCES Unit_Types(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------------------------
-- 4. KHO PHÒNG & GIÁ THEO NGÀY (INVENTORY)
-- ------------------------------------------------------------------------------
CREATE TABLE Unit_Inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    unit_type_id INT NOT NULL,
    target_date DATE NOT NULL,
    available_units INT NOT NULL, 
    price DECIMAL(10, 2) NOT NULL, 
    UNIQUE KEY (unit_type_id, target_date),
    FOREIGN KEY (unit_type_id) REFERENCES Unit_Types(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------------------------
-- 5. QUẢN LÝ ĐẶT PHÒNG & THANH TOÁN (BOOKINGS)
-- ------------------------------------------------------------------------------

CREATE TABLE Promotions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    discount_percent DECIMAL(5,2) NOT NULL,
    valid_from DATE,
    valid_until DATE,
    max_usage INT DEFAULT 100
);

CREATE TABLE Bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_reference VARCHAR(20) UNIQUE NOT NULL, 
    user_id INT NOT NULL,
    property_id INT NOT NULL,
    promotion_id INT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status ENUM('pending_payment', 'confirmed', 'cancelled', 'completed') DEFAULT 'pending_payment',
    special_requests TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE RESTRICT,
    FOREIGN KEY (property_id) REFERENCES Properties(id) ON DELETE RESTRICT,
    FOREIGN KEY (promotion_id) REFERENCES Promotions(id) ON DELETE SET NULL
);

CREATE TABLE Booking_Details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    unit_type_id INT NOT NULL,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    units_booked INT NOT NULL DEFAULT 1,
    subtotal DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES Bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (unit_type_id) REFERENCES Unit_Types(id) ON DELETE RESTRICT
);

CREATE TABLE Payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL UNIQUE,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('credit_card', 'paypal', 'bank_transfer', 'momo', 'cash') NOT NULL,
    payment_status ENUM('pending', 'success', 'failed', 'refunded') DEFAULT 'pending',
    transaction_id VARCHAR(100),
    paid_at TIMESTAMP NULL,
    FOREIGN KEY (booking_id) REFERENCES Bookings(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------------------------
-- 6. ĐÁNH GIÁ (REVIEWS)
-- ------------------------------------------------------------------------------
CREATE TABLE Reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL UNIQUE,
    user_id INT NOT NULL,
    property_id INT NOT NULL,
    cleanliness_rating INT CHECK (cleanliness_rating BETWEEN 1 AND 10),
    location_rating INT CHECK (location_rating BETWEEN 1 AND 10),
    service_rating INT CHECK (service_rating BETWEEN 1 AND 10),
    average_rating DECIMAL(3,1) GENERATED ALWAYS AS ((cleanliness_rating + location_rating + service_rating) / 3) STORED,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES Bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (property_id) REFERENCES Properties(id) ON DELETE CASCADE
);

-- ==============================================================================
-- 7. [QUAN TRỌNG] TẠO VIEW CHO API TRẢ VỀ DANH SÁCH KHÁCH SẠN
-- ==============================================================================
-- Bảng ảo này sẽ tự động tính toán giá thấp nhất, điểm số trung bình, và số lượng review
-- Backend Python chỉ cần: SELECT * FROM vw_Hotel_API_List WHERE city_id = '1_318'

CREATE VIEW vw_Hotel_API_List AS
SELECT 
    p.id AS id, -- Backend có thể ép kiểu sang String để trả về App
    p.name,
    p.address,
    p.city,
    p.city_id,
    p.star_rating,
    p.is_preferred,
    p.is_active AS is_available,
    p.latitude,
    p.longitude,
    
    -- Lấy ảnh chính của khách sạn
    (SELECT image_url FROM Property_Images pi WHERE pi.property_id = p.id AND pi.is_primary = TRUE LIMIT 1) AS image_url,
    
    -- Lấy giá thấp nhất của khách sạn này (từ các phòng đang có sẵn trong hôm nay trở đi)
    COALESCE((
        SELECT MIN(ui.price) 
        FROM Unit_Inventory ui 
        JOIN Unit_Types ut ON ui.unit_type_id = ut.id 
        WHERE ut.property_id = p.id AND ui.available_units > 0 AND ui.target_date >= CURRENT_DATE
    ), 0) AS price,
    
    -- Tính điểm trung bình
    COALESCE((
        SELECT ROUND(AVG(r.average_rating), 1) 
        FROM Reviews r 
        WHERE r.property_id = p.id
    ), 0.0) AS score,
    
    -- Đếm số lượng đánh giá
    COALESCE((
        SELECT COUNT(r.id) 
        FROM Reviews r 
        WHERE r.property_id = p.id
    ), 0) AS review_count

FROM Properties p;