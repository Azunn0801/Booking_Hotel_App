package com.example.android_app.models;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;

public class Room implements Serializable {
    @SerializedName("id")
    private String id;

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

    @SerializedName("breakfast_included")
    private boolean breakfastIncluded;

    @SerializedName("cancellation_policy")
    private String cancellationPolicy;

    @SerializedName("cancellation_policy_type")
    private int cancellationPolicyType;

    @SerializedName("is_free_cancellation")
    private boolean isFreeCancellation;

    @SerializedName("remain_room")
    private int remainRoom;

    @SerializedName("room_occupancy_description")
    private String roomOccupancyDescription;

    @SerializedName("images")
    private java.util.List<String> images;

    @SerializedName("check_in")
    private String checkIn;

    @SerializedName("check_out")
    private String checkOut;

    public Room() {}

    // Getter và Setter
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

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

    public boolean isBreakfastIncluded() { return breakfastIncluded; }
    public void setBreakfastIncluded(boolean breakfastIncluded) { this.breakfastIncluded = breakfastIncluded; }

    public String getCancellationPolicy() { return cancellationPolicy; }
    public void setCancellationPolicy(String cancellationPolicy) { this.cancellationPolicy = cancellationPolicy; }

    public int getCancellationPolicyType() { return cancellationPolicyType; }
    public void setCancellationPolicyType(int cancellationPolicyType) { this.cancellationPolicyType = cancellationPolicyType; }

    public boolean isFreeCancellation() { return isFreeCancellation; }
    public void setFreeCancellation(boolean freeCancellation) { this.isFreeCancellation = freeCancellation; }

    public int getRemainRoom() { return remainRoom; }
    public void setRemainRoom(int remainRoom) { this.remainRoom = remainRoom; }

    public String getRoomOccupancyDescription() { return roomOccupancyDescription; }
    public void setRoomOccupancyDescription(String roomOccupancyDescription) { this.roomOccupancyDescription = roomOccupancyDescription; }

    public java.util.List<String> getImages() { return images; }
    public void setImages(java.util.List<String> images) { this.images = images; }

    public String getCheckIn() { return checkIn; }
    public void setCheckIn(String checkIn) { this.checkIn = checkIn; }

    public String getCheckOut() { return checkOut; }
    public void setCheckOut(String checkOut) { this.checkOut = checkOut; }
}