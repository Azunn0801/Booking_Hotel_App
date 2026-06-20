package com.example.android_app.models;

import com.google.gson.annotations.SerializedName;

public class ProfileUpdateRequest {
    @SerializedName("full_name")
    private String fullName;

    public ProfileUpdateRequest(String fullName) {
        this.fullName = fullName;
    }

    public String getFullName() { return fullName; }
}
