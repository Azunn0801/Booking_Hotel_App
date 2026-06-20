package com.example.android_app.models;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;

public class Property implements Serializable {

    private boolean isLoading = false;

    @SerializedName("id")
    private String id;

    @SerializedName("name")
    private String name;

    @SerializedName("propertyType")
    private String propertyType; // "hotel", "apartment", "villa"

    @SerializedName("propertyTypeName")
    private String propertyTypeName;

    @SerializedName("address")
    private String address;

    @SerializedName("city")
    private String city;

    @SerializedName("starRating")
    private float starRating;

    @SerializedName("score")
    private double score;

    @SerializedName("reviewCount")
    private int reviewCount;

    @SerializedName("imageUrl")
    private String imageUrl;

    @SerializedName("price")
    private double price;

    @SerializedName("originalPrice")
    private double originalPrice;

    @SerializedName("discountPercent")
    private int discountPercent;

    @SerializedName("latitude")
    private double latitude;

    @SerializedName("longitude")
    private double longitude;

    @SerializedName("isPreferred")
    private boolean isPreferred;

    @SerializedName("isAvailable")
    private boolean isAvailable;

    @SerializedName("reviewQuote")
    private String reviewQuote;

    @SerializedName("distanceDescription")
    private String distanceDescription;

    // Loading constructor
    public Property(boolean isLoading) {
        this.isLoading = isLoading;
    }

    public Property() {}

    public boolean isLoading() { return isLoading; }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getPropertyType() { return propertyType; }
    public void setPropertyType(String propertyType) { this.propertyType = propertyType; }

    public String getPropertyTypeName() { return propertyTypeName; }
    public void setPropertyTypeName(String propertyTypeName) { this.propertyTypeName = propertyTypeName; }

    public String getAddress() { return address; }
    public void setAddress(String address) { this.address = address; }

    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }

    public float getStarRating() { return starRating; }
    public void setStarRating(float starRating) { this.starRating = starRating; }

    public double getScore() { return score; }
    public void setScore(double score) { this.score = score; }

    public int getReviewCount() { return reviewCount; }
    public void setReviewCount(int reviewCount) { this.reviewCount = reviewCount; }

    public String getImageUrl() { return imageUrl; }
    public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }

    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }

    public double getOriginalPrice() { return originalPrice; }
    public void setOriginalPrice(double originalPrice) { this.originalPrice = originalPrice; }

    public int getDiscountPercent() { return discountPercent; }
    public void setDiscountPercent(int discountPercent) { this.discountPercent = discountPercent; }

    public double getLatitude() { return latitude; }
    public void setLatitude(double latitude) { this.latitude = latitude; }

    public double getLongitude() { return longitude; }
    public void setLongitude(double longitude) { this.longitude = longitude; }

    public boolean isPreferred() { return isPreferred; }
    public void setPreferred(boolean preferred) { isPreferred = preferred; }

    public boolean isAvailable() { return isAvailable; }
    public void setAvailable(boolean available) { isAvailable = available; }

    public String getReviewQuote() { return reviewQuote; }
    public void setReviewQuote(String reviewQuote) { this.reviewQuote = reviewQuote; }

    public String getDistanceDescription() { return distanceDescription; }
    public void setDistanceDescription(String distanceDescription) { this.distanceDescription = distanceDescription; }
}
