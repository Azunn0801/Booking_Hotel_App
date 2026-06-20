package com.example.android_app.models;

import com.google.gson.annotations.SerializedName;

public class PromoApplyResponse {

    @SerializedName("code")
    private String code;

    @SerializedName("title")
    private String title;

    @SerializedName("discount_percent")
    private double discountPercent;

    @SerializedName("discount_amount")
    private double discountAmount;

    @SerializedName("original_price")
    private double originalPrice;

    @SerializedName("final_price")
    private double finalPrice;

    // Getters
    public String getCode() { return code; }
    public String getTitle() { return title; }
    public double getDiscountPercent() { return discountPercent; }
    public double getDiscountAmount() { return discountAmount; }
    public double getOriginalPrice() { return originalPrice; }
    public double getFinalPrice() { return finalPrice; }
}
