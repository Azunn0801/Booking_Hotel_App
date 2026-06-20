package com.example.android_app.models;

import com.google.gson.annotations.SerializedName;

public class LoginResponse {
    @SerializedName("message")
    private String message;

    @SerializedName("user_id")
    private int userId;

    @SerializedName("full_name")
    private String fullName;

    public String getMessage() { return message; }
    public int getUserId() { return userId; }
    public String getFullName() { return fullName; }
}
