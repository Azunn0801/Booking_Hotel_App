package com.example.android_app.models;

import com.google.gson.annotations.SerializedName;

public class BookingRequest {

    @SerializedName("user_id")
    private int userId;

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

    @SerializedName("promotion_code")
    private String promotionCode;

    public BookingRequest(int userId, String propertyId, String propertyName,
                          String propertyType, String propertyImage,
                          String checkinDate, String checkoutDate,
                          double totalPrice, double originalPrice,
                          double discountAmount, String promotionCode) {
        this.userId = userId;
        this.propertyId = propertyId;
        this.propertyName = propertyName;
        this.propertyType = propertyType;
        this.propertyImage = propertyImage;
        this.checkinDate = checkinDate;
        this.checkoutDate = checkoutDate;
        this.totalPrice = totalPrice;
        this.originalPrice = originalPrice;
        this.discountAmount = discountAmount;
        this.promotionCode = promotionCode;
    }

    public int getUserId() { return userId; }
    public String getPropertyId() { return propertyId; }
    public String getPropertyName() { return propertyName; }
    public String getPropertyType() { return propertyType; }
    public String getPropertyImage() { return propertyImage; }
    public String getCheckinDate() { return checkinDate; }
    public String getCheckoutDate() { return checkoutDate; }
    public double getTotalPrice() { return totalPrice; }
    public double getOriginalPrice() { return originalPrice; }
    public double getDiscountAmount() { return discountAmount; }
    public String getPromotionCode() { return promotionCode; }
}
