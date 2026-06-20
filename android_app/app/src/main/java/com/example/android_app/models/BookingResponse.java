package com.example.android_app.models;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;

public class BookingResponse implements Serializable {

    @SerializedName("id")
    private int id;

    @SerializedName("property_id")
    private String propertyId;

    @SerializedName("property_name")
    private String propertyName;

    @SerializedName("property_type")
    private String propertyType;

    @SerializedName("property_image")
    private String propertyImage;

    @SerializedName("checkin_date")
    private String checkinDate;

    @SerializedName("checkout_date")
    private String checkoutDate;

    @SerializedName("total_price")
    private double totalPrice;

    @SerializedName("original_price")
    private double originalPrice;

    @SerializedName("discount_amount")
    private double discountAmount;

    @SerializedName("status")
    private String status;

    @SerializedName("created_at")
    private String createdAt;

    // Getters
    public int getId() { return id; }
    public String getPropertyId() { return propertyId; }
    public String getPropertyName() { return propertyName; }
    public String getPropertyType() { return propertyType; }
    public String getPropertyImage() { return propertyImage; }
    public String getCheckinDate() { return checkinDate; }
    public String getCheckoutDate() { return checkoutDate; }
    public double getTotalPrice() { return totalPrice; }
    public double getOriginalPrice() { return originalPrice; }
    public double getDiscountAmount() { return discountAmount; }
    public String getStatus() { return status; }
    public String getCreatedAt() { return createdAt; }
}
