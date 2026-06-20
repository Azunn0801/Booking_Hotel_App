package com.example.android_app.models;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;
import java.util.List;
import java.util.Map;

public class PropertyDetail implements Serializable {

    @SerializedName("id")
    private String id;

    @SerializedName("name")
    private String name;

    @SerializedName("propertyType")
    private String propertyType;

    @SerializedName("starRating")
    private float starRating;

    @SerializedName("description")
    private String description;

    @SerializedName("imageUrls")
    private List<ImageInfo> imageUrls;

    @SerializedName("reviewSummary")
    private Map<String, Object> reviewSummary;

    @SerializedName("reviewSnippets")
    private List<ReviewSnippet> reviewSnippets;

    @SerializedName("favoriteFeatures")
    private List<FeatureInfo> favoriteFeatures;

    @SerializedName("nearbyPlaces")
    private List<PlaceInfo> nearbyPlaces;

    @SerializedName("topPlaces")
    private List<PlaceInfo> topPlaces;

    @SerializedName("address")
    private AddressInfo address;

    @SerializedName("latitude")
    private double latitude;

    @SerializedName("longitude")
    private double longitude;

    @SerializedName("reviewBreakdown")
    private ReviewBreakdown reviewBreakdown;

    @SerializedName("featureGroups")
    private List<FeatureGroup> featureGroups;

    @SerializedName("checkIn")
    private String checkIn;

    @SerializedName("checkOut")
    private String checkOut;

    // Getters
    public String getId() { return id; }
    public String getName() { return name; }
    public String getPropertyType() { return propertyType; }
    public float getStarRating() { return starRating; }
    public String getDescription() { return description; }
    public List<ImageInfo> getImageUrls() { return imageUrls; }
    public Map<String, Object> getReviewSummary() { return reviewSummary; }
    public List<ReviewSnippet> getReviewSnippets() { return reviewSnippets; }
    public List<FeatureInfo> getFavoriteFeatures() { return favoriteFeatures; }
    public List<PlaceInfo> getNearbyPlaces() { return nearbyPlaces; }
    public List<PlaceInfo> getTopPlaces() { return topPlaces; }
    public AddressInfo getAddress() { return address; }
    public double getLatitude() { return latitude; }
    public double getLongitude() { return longitude; }
    public ReviewBreakdown getReviewBreakdown() { return reviewBreakdown; }
    public List<FeatureGroup> getFeatureGroups() { return featureGroups; }
    public String getCheckIn() { return checkIn; }
    public String getCheckOut() { return checkOut; }

    // Inner classes
    public static class ImageInfo implements Serializable {
        @SerializedName("url")
        private String url;
        @SerializedName("caption")
        private String caption;
        @SerializedName("category")
        private String category;

        public String getUrl() { return url; }
        public String getCaption() { return caption; }
        public String getCategory() { return category; }
    }

    public static class ReviewSnippet implements Serializable {
        @SerializedName("text")
        private String text;
        @SerializedName("rating")
        private double rating;
        @SerializedName("reviewer")
        private String reviewer;
        @SerializedName("date")
        private String date;
        @SerializedName("country")
        private String country;

        public String getText() { return text; }
        public double getRating() { return rating; }
        public String getReviewer() { return reviewer; }
        public String getDate() { return date; }
        public String getCountry() { return country; }
    }

    public static class FeatureInfo implements Serializable {
        @SerializedName("id")
        private int id;
        @SerializedName("name")
        private String name;
        @SerializedName("symbol")
        private String symbol;

        public int getId() { return id; }
        public String getName() { return name; }
        public String getSymbol() { return symbol; }
    }

    public static class PlaceInfo implements Serializable {
        @SerializedName("name")
        private String name;
        @SerializedName("distance")
        private double distance;
        @SerializedName("type")
        private String type;

        public String getName() { return name; }
        public double getDistance() { return distance; }
        public String getType() { return type; }
    }

    public static class AddressInfo implements Serializable {
        @SerializedName("street")
        private String street;
        @SerializedName("area")
        private String area;
        @SerializedName("city")
        private String city;
        @SerializedName("country")
        private String country;
        @SerializedName("postalCode")
        private String postalCode;

        public String getStreet() { return street; }
        public String getArea() { return area; }
        public String getCity() { return city; }
        public String getCountry() { return country; }
        public String getPostalCode() { return postalCode; }
    }

    public static class ReviewBreakdown implements Serializable {
        @SerializedName("allGuest")
        private DemographicGroup allGuest;
        @SerializedName("groups")
        private List<DemographicGroup> groups;

        public DemographicGroup getAllGuest() { return allGuest; }
        public List<DemographicGroup> getGroups() { return groups; }
    }

    public static class DemographicGroup implements Serializable {
        @SerializedName("id")
        private int id;
        @SerializedName("name")
        private String name;
        @SerializedName("reviewCount")
        private int reviewCount;
        @SerializedName("grades")
        private Map<String, Double> grades;

        public int getId() { return id; }
        public String getName() { return name; }
        public int getReviewCount() { return reviewCount; }
        public Map<String, Double> getGrades() { return grades; }
    }

    public static class FeatureGroup implements Serializable {
        @SerializedName("id")
        private String id;
        @SerializedName("name")
        private String name;
        @SerializedName("order")
        private int order;
        @SerializedName("features")
        private List<Feature> features;

        public String getId() { return id; }
        public String getName() { return name; }
        public int getOrder() { return order; }
        public List<Feature> getFeatures() { return features; }
    }

    public static class Feature implements Serializable {
        @SerializedName("id")
        private String id;
        @SerializedName("name")
        private String name;
        @SerializedName("symbol")
        private String symbol;
        @SerializedName("available")
        private boolean available;
        @SerializedName("order")
        private int order;

        public String getId() { return id; }
        public String getName() { return name; }
        public String getSymbol() { return symbol; }
        public boolean isAvailable() { return available; }
        public int getOrder() { return order; }
    }
}
