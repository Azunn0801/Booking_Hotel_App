package com.example.android_app.models;

import com.google.gson.annotations.SerializedName;

public class PromoApplyRequest {

    @SerializedName("code")
    private String code;

    @SerializedName("total_price")
    private double totalPrice;

    public PromoApplyRequest(String code, double totalPrice) {
        this.code = code;
        this.totalPrice = totalPrice;
    }

    public String getCode() { return code; }
    public double getTotalPrice() { return totalPrice; }
}
