package com.example.android_app.models;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;

public class Hotel implements Serializable {

    private boolean isLoading = false;

    @SerializedName("id")
    private String id; // FIX: Phải là String vì id có dạng "1_318"

    @SerializedName("name") // Kiểm tra lại nếu Python trả về "hotel_name" thì sửa thành "hotel_name"
    private String name;

    @SerializedName("address")
    private String address;

    @SerializedName("city")
    private String city;

    @SerializedName("price")
    private double price;

    @SerializedName("city_id")
    private String cityId;

    @SerializedName("star_rating")
    private float starRating;

    @SerializedName("image_url")
    private String imageUrl;

    @SerializedName("is_available")
    private boolean isAvailable;

    @SerializedName("score")
    private double score; // Ví dụ: 9.3

    @SerializedName("review_count") // FIX: Ánh xạ từ review_count của Python
    private int reviewCount;

    @SerializedName("is_preferred") // FIX: Ánh xạ từ is_preferred
    private boolean isPreferred;

    // Constructor cho Loading/Skeleton
    public Hotel(boolean isLoading) {
        this.isLoading = isLoading;
    }

    // Constructor đầy đủ
    public Hotel(String name, String address, double price, float starRating, String imageUrl, double score, int reviewCount, boolean isPreferred) {
        this.name = name;
        this.address = address;
        this.price = price;
        this.starRating = starRating;
        this.imageUrl = imageUrl;
        this.score = score;
        this.reviewCount = reviewCount;
        this.isPreferred = isPreferred;
    }

    public boolean isLoading() { return isLoading; }

    // GETTER & SETTER ĐÃ CHUẨN HÓA KIỂU DỮ LIỆU
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getAddress() { return address; }
    public void setAddress(String address) { this.address = address; }

    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; } // FIX: match double

    public float getStarRating() { return starRating; }
    public void setStarRating(float starRating) { this.starRating = starRating; } // FIX: match float

    public String getImageUrl() { return imageUrl; }
    public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }

    public double getScore() { return score; }
    public void setScore(double score) { this.score = score; }

    public int getReviewCount() { return reviewCount; }
    public void setReviewCount(int reviewCount) { this.reviewCount = reviewCount; }

    public boolean isPreferred() { return isPreferred; }
    public void setPreferred(boolean preferred) { isPreferred = preferred; }

    public boolean isAvailable() { return isAvailable; }
    public void setAvailable(boolean available) { isAvailable = available; }

    // Thêm vào Hotel.java
    @SerializedName("latitude")
    private double latitude;

    @SerializedName("longitude")
    private double longitude;

    // Getter và Setter
    public double getLatitude() { return latitude; }
    public void setLatitude(double latitude) { this.latitude = latitude; }
    public double getLongitude() { return longitude; }
    public void setLongitude(double longitude) { this.longitude = longitude; }
}