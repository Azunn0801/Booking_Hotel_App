package com.example.android_app.models;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;

public class Room implements Serializable {
    private int id;

    @SerializedName("hotel_id")
    private int hotelId;

    @SerializedName("room_name")
    private String roomName;

    private float price; // Giá mỗi đêm

    private String amenities; // Các tiện nghi như: "35,43" (Wifi, AC...)

    @SerializedName("is_available")
    private boolean isAvailable;

    @com.google.gson.annotations.SerializedName("original_price")
    private double originalPrice;

    @com.google.gson.annotations.SerializedName("discount_percent")
    private int discountPercent;

    public Room() {}

    // Getter và Setter
    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public int getHotelId() { return hotelId; }
    public void setHotelId(int hotelId) { this.hotelId = hotelId; }

    public String getRoomName() { return roomName; }
    public void setRoomName(String roomName) { this.roomName = roomName; }

    public float getPrice() { return price; }
    public void setPrice(float price) { this.price = price; }

    public String getAmenities() { return amenities; }
    public void setAmenities(String amenities) { this.amenities = amenities; }

    public boolean isAvailable() { return isAvailable; }
    public void setAvailable(boolean available) { isAvailable = available; }

    public double getOriginalPrice() {
        return originalPrice;
    }

    public int getDiscountPercent() {
        return discountPercent;
    }

    // Nếu bạn cần Setter thì có thể thêm vào:
    public void setOriginalPrice(double originalPrice) {
        this.originalPrice = originalPrice;
    }

    public void setDiscountPercent(int discountPercent) {
        this.discountPercent = discountPercent;
    }
}