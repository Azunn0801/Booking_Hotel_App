package com.example.android_app.models;

import com.google.gson.annotations.SerializedName;

public class Language {
    @SerializedName("name")
    private String name;

    @SerializedName("code")
    private String code;

    public String getName() { return name; }
    public String getCode() { return code; }
}
