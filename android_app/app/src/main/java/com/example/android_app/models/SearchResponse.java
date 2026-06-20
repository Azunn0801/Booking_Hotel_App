package com.example.android_app.models;

import com.google.gson.annotations.SerializedName;
import java.util.List;

public class SearchResponse {
    @SerializedName("properties")
    private List<Property> properties;

    @SerializedName("filters")
    private List<FilterGroup> filters;

    @SerializedName("totalCount")
    private int totalCount;

    public List<Property> getProperties() { return properties; }
    public List<FilterGroup> getFilters() { return filters; }
    public int getTotalCount() { return totalCount; }

    public static class FilterGroup {
        @SerializedName("matrixGroup")
        private String matrixGroup;

        @SerializedName("matrixItemResults")
        private List<FilterItem> matrixItemResults;

        public String getMatrixGroup() { return matrixGroup; }
        public List<FilterItem> getMatrixItemResults() { return matrixItemResults; }
    }

    public static class FilterItem {
        @SerializedName("id")
        private String id;

        @SerializedName("filterKey")
        private String filterKey;

        @SerializedName("name")
        private String name;

        @SerializedName("count")
        private int count;

        public String getId() { return id; }
        public String getFilterKey() { return filterKey; }
        public String getName() { return name; }
        public int getCount() { return count; }
    }
}
