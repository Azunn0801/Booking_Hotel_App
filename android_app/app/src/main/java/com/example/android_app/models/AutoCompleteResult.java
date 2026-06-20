package com.example.android_app.models;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;

public class AutoCompleteResult implements Serializable {
    @SerializedName("id")
    private int id;

    @SerializedName("name")
    private String name;

    @SerializedName("type")
    private String type;

    @SerializedName("city_id")
    private Integer cityId;

    @SerializedName("city_name")
    private String cityName;

    @SerializedName("country_name")
    private String countryName;

    @SerializedName("latitude")
    private double latitude;

    @SerializedName("longitude")
    private double longitude;

    @SerializedName("active_hotels")
    private int activeHotels;

    @SerializedName("image_url")
    private String imageUrl;

    @SerializedName("state_id")
    private Integer stateId;

    @SerializedName("state_name")
    private String stateName;

    // Getters
    public int getId() { return id; }
    public String getName() { return name; }
    public String getType() { return type; }
    public Integer getCityId() { return cityId; }
    public String getCityName() { return cityName; }
    public String getCountryName() { return countryName; }
    public double getLatitude() { return latitude; }
    public double getLongitude() { return longitude; }
    public int getActiveHotels() { return activeHotels; }
    public String getImageUrl() { return imageUrl; }
    public Integer getStateId() { return stateId; }
    public String getStateName() { return stateName; }

    // Returns city_id as string for search (format: "countryId_cityId")
    public String getSearchId() {
        if (cityId != null) {
            return "1_" + cityId;
        }
        return String.valueOf(id);
    }
}
