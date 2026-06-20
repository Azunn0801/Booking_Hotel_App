package com.example.android_app.models;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;

public class Promotion implements Serializable {

    @SerializedName("id")
    private int id;

    @SerializedName("code")
    private String code;

    @SerializedName("title")
    private String title;

    @SerializedName("description")
    private String description;

    @SerializedName("discount_percent")
    private double discountPercent;

    @SerializedName("valid_until")
    private String validUntil;

    @SerializedName("remaining_uses")
    private int remainingUses;

    @SerializedName("is_valid")
    private boolean isValid;

    @SerializedName("image_url")
    private String imageUrl;

    // Getters & Setters
    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public String getCode() { return code; }
    public void setCode(String code) { this.code = code; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public double getDiscountPercent() { return discountPercent; }
    public void setDiscountPercent(double discountPercent) { this.discountPercent = discountPercent; }

    public String getValidUntil() { return validUntil; }
    public void setValidUntil(String validUntil) { this.validUntil = validUntil; }

    public int getRemainingUses() { return remainingUses; }
    public void setRemainingUses(int remainingUses) { this.remainingUses = remainingUses; }

    public boolean isValid() { return isValid; }
    public void setValid(boolean valid) { isValid = valid; }

    public String getImageUrl() { return imageUrl; }
    public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }
}
