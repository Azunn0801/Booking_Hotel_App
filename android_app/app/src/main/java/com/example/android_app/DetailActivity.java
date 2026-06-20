package com.example.android_app;

import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Bundle;
import android.text.Html;
import android.text.Spanned;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.RatingBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;
import com.example.android_app.adapters.RoomAdapter;
import com.example.android_app.models.Property;
import com.example.android_app.models.PropertyDetail;
import com.example.android_app.models.Room;
import com.example.android_app.network.ApiClient;
import com.example.android_app.network.ApiService;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class DetailActivity extends AppCompatActivity {
    private RecyclerView rvRooms;
    private RoomAdapter roomAdapter;
    private List<Room> roomList = new ArrayList<>();
    private Property property;
    private String checkInDate;
    private String checkOutDate;

    // Translation Map for common facility keys
    private static final Map<String, String> translationMap = new HashMap<>();
    static {
        translationMap.put("wifi", "Wi-Fi miễn phí");
        translationMap.put("internet", "Internet");
        translationMap.put("pool", "Hồ bơi");
        translationMap.put("gym", "Phòng thể hình");
        translationMap.put("spa", "Spa / Massage");
        translationMap.put("restaurant", "Nhà hàng");
        translationMap.put("bar", "Quầy bar");
        translationMap.put("ac", "Điều hòa nhiệt độ");
        translationMap.put("tv", "Tivi");
        translationMap.put("elevator", "Thang máy");
        translationMap.put("breakfast", "Bữa sáng");
        translationMap.put("shuttle", "Đưa đón sân bay");
        translationMap.put("kitchen", "Bếp");
        translationMap.put("fridge", "Tủ lạnh");
        translationMap.put("beach", "Gần bãi biển");
        translationMap.put("garden", "Sân vườn");
        translationMap.put("terrace", "Ban công / Sân thượng");
        translationMap.put("safe", "Két an toàn");
        translationMap.put("bathroom", "Phòng tắm");
        translationMap.put("bedroom", "Phòng ngủ");
        translationMap.put("entertainment", "Giải trí");
        translationMap.put("food and drinks", "Đồ ăn & Thức uống");
        translationMap.put("services", "Dịch vụ & Tiện ích");
        translationMap.put("safety", "An toàn & An ninh");
        translationMap.put("laundry", "Giặt ủi");
        translationMap.put("parking", "Bãi đậu xe");
        translationMap.put("transportation", "Phương tiện di chuyển");
        translationMap.put("wellness", "Sức khỏe & Làm đẹp");
    }

    private String translate(String key) {
        if (key == null) return "N/A";
        String lowerKey = key.toLowerCase();
        if (translationMap.containsKey(lowerKey)) {
            return translationMap.get(lowerKey);
        }
        return key;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_detail);

        property = (Property) getIntent().getSerializableExtra("property_data");
        checkInDate = getIntent().getStringExtra("checkin_date");
        checkOutDate = getIntent().getStringExtra("checkout_date");

        if (property == null) {
            Toast.makeText(this, "Không có dữ liệu khách sạn!", Toast.LENGTH_SHORT).show();
            finish();
            return;
        }

        initViews();
        loadPropertyDetails();
        loadRooms();
    }

    private void initViews() {
        ImageView img = findViewById(R.id.imgHotelDetail);
        TextView name = findViewById(R.id.tvDetailName);
        TextView address = findViewById(R.id.tvDetailAddress);
        RatingBar rating = findViewById(R.id.detailRatingBar);

        name.setText(property.getName());
        rating.setRating(property.getStarRating());
        
        // Initial image from search
        Glide.with(this)
                .load(property.getImageUrl())
                .placeholder(android.R.color.darker_gray)
                .into(img);

        if (address != null) address.setText(property.getAddress());

        findViewById(R.id.btnBack).setOnClickListener(v -> finish());

        rvRooms = findViewById(R.id.rvRooms);
        // [FIX] Ensure LayoutManager is set before adapter
        rvRooms.setLayoutManager(new LinearLayoutManager(this));
        roomAdapter = new RoomAdapter(this, roomList, property, checkInDate, checkOutDate);
        rvRooms.setAdapter(roomAdapter);
    }

    private void loadPropertyDetails() {
        ApiService apiService = ApiClient.getClient().create(ApiService.class);
        apiService.getPropertyDetails(property.getId()).enqueue(new Callback<PropertyDetail>() {
            @Override
            public void onResponse(@NonNull Call<PropertyDetail> call, @NonNull Response<PropertyDetail> response) {
                if (response.isSuccessful() && response.body() != null) {
                    PropertyDetail detail = response.body();

                    // Update UI with rich details
                    TextView tvName = findViewById(R.id.tvDetailName);
                    if (tvName != null) tvName.setText(detail.getName());
                    
                    RatingBar rb = findViewById(R.id.detailRatingBar);
                    if (rb != null) rb.setRating(detail.getStarRating());

                    // Render Description as HTML
                    TextView tvDescription = findViewById(R.id.tvDetailDescription);
                    if (tvDescription != null && detail.getDescription() != null && !detail.getDescription().isEmpty()) {
                        tvDescription.setVisibility(View.VISIBLE);
                        Spanned formattedDesc = Html.fromHtml(detail.getDescription(), Html.FROM_HTML_MODE_COMPACT);
                        tvDescription.setText(formattedDesc);
                    }

                    // Score Box
                    TextView tvScore = findViewById(R.id.tvDetailScore);
                    if (tvScore != null && detail.getReviewSummary() != null) {
                        Object avgScore = detail.getReviewSummary().get("overall");
                        if (avgScore != null) {
                            tvScore.setText(String.valueOf(avgScore));
                        }
                    }

                    // Check-in/out
                    TextView tvCheckIn = findViewById(R.id.tvCheckInTime);
                    TextView tvCheckOut = findViewById(R.id.tvCheckOutTime);
                    if (tvCheckIn != null && detail.getCheckIn() != null) tvCheckIn.setText(detail.getCheckIn());
                    if (tvCheckOut != null && detail.getCheckOut() != null) tvCheckOut.setText(detail.getCheckOut());

                    // Review Breakdown
                    if (detail.getReviewBreakdown() != null) {
                        renderDemographics(detail.getReviewBreakdown());
                    }

                    // Review Snippets
                    if (detail.getReviewSnippets() != null && !detail.getReviewSnippets().isEmpty()) {
                        renderReviewSnippets(detail.getReviewSnippets());
                    }

                    // Features
                    if (detail.getFeatureGroups() != null && !detail.getFeatureGroups().isEmpty()) {
                        renderFeatureGroups(detail.getFeatureGroups());
                    }

                    // Nearby
                    if (detail.getNearbyPlaces() != null && !detail.getNearbyPlaces().isEmpty()) {
                        renderNearbyPlaces(detail.getNearbyPlaces());
                    }
                    
                    // Address
                    TextView tvAddr = findViewById(R.id.tvDetailAddress);
                    if (tvAddr != null && detail.getAddress() != null) {
                        String fullAddr = detail.getAddress().getStreet() + ", " + detail.getAddress().getCity();
                        tvAddr.setText(fullAddr);
                    }
                }
            }

            @Override
            public void onFailure(@NonNull Call<PropertyDetail> call, @NonNull Throwable t) {
                Log.e("DETAIL_ERROR", "Failed to load details", t);
            }
        });
    }

    private void loadRooms() {
        String checkin = (checkInDate != null && !checkInDate.isEmpty()) ? checkInDate : "2026-06-01";
        String checkout = (checkOutDate != null && !checkOutDate.isEmpty()) ? checkOutDate : "2026-06-02";

        ApiService apiService = ApiClient.getClient().create(ApiService.class);
        apiService.getPropertyRooms(property.getId(), checkin, checkout).enqueue(new Callback<List<Room>>() {
            @Override
            public void onResponse(@NonNull Call<List<Room>> call, @NonNull Response<List<Room>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    roomList.clear();
                    roomList.addAll(response.body());
                    roomAdapter.notifyDataSetChanged();
                } else {
                    Log.e("ROOMS_ERROR", "Response failed: " + response.code());
                }
            }

            @Override
            public void onFailure(@NonNull Call<List<Room>> call, @NonNull Throwable t) {
                Log.e("ROOMS_ERROR", "Failed to load rooms", t);
            }
        });
    }

    private void renderDemographics(PropertyDetail.ReviewBreakdown breakdown) {
        if (breakdown.getGroups() == null || breakdown.getGroups().isEmpty()) return;

        findViewById(R.id.tvDemographicsTitle).setVisibility(View.VISIBLE);
        findViewById(R.id.hsvDemographics).setVisibility(View.VISIBLE);
        findViewById(R.id.dividerDemographics).setVisibility(View.VISIBLE);

        LinearLayout layout = findViewById(R.id.layoutDemographics);
        layout.removeAllViews();

        for (PropertyDetail.DemographicGroup group : breakdown.getGroups()) {
            LinearLayout item = new LinearLayout(this);
            item.setOrientation(LinearLayout.VERTICAL);
            item.setPadding(32, 24, 32, 24);
            item.setBackgroundResource(R.drawable.bg_search_bar);
            LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
            params.setMargins(0, 0, 16, 0);
            item.setLayoutParams(params);

            TextView tvName = new TextView(this);
            tvName.setText(group.getName());
            tvName.setTextSize(14);
            tvName.setTextColor(Color.DKGRAY);
            item.addView(tvName);

            if (group.getGrades() != null && group.getGrades().containsKey("overall")) {
                TextView tvScore = new TextView(this);
                tvScore.setText(String.format(java.util.Locale.US, "%.1f/10", group.getGrades().get("overall")));
                tvScore.setTextSize(16);
                tvScore.setTypeface(null, Typeface.BOLD);
                tvScore.setTextColor(Color.parseColor("#0073BB"));
                tvScore.setPadding(0, 8, 0, 0);
                item.addView(tvScore);
            }
            layout.addView(item);
        }
    }

    private void renderReviewSnippets(List<PropertyDetail.ReviewSnippet> snippets) {
        findViewById(R.id.tvReviewSnippetsTitle).setVisibility(View.VISIBLE);
        findViewById(R.id.layoutReviewSnippets).setVisibility(View.VISIBLE);
        findViewById(R.id.dividerReviews).setVisibility(View.VISIBLE);

        LinearLayout layout = findViewById(R.id.layoutReviewSnippets);
        layout.removeAllViews();

        for (PropertyDetail.ReviewSnippet snippet : snippets) {
            LinearLayout item = new LinearLayout(this);
            item.setOrientation(LinearLayout.VERTICAL);
            item.setPadding(0, 16, 0, 16);
            
            TextView tvQuote = new TextView(this);
            tvQuote.setText("\"" + snippet.getText() + "\"");
            tvQuote.setTextSize(14);
            tvQuote.setTypeface(null, Typeface.ITALIC);
            tvQuote.setTextColor(Color.BLACK);
            item.addView(tvQuote);

            TextView tvAuthor = new TextView(this);
            tvAuthor.setText("- " + snippet.getReviewer() + " (" + snippet.getCountry() + ")");
            tvAuthor.setTextSize(12);
            tvAuthor.setTextColor(Color.GRAY);
            tvAuthor.setPadding(0, 4, 0, 0);
            item.addView(tvAuthor);

            View divider = new View(this);
            divider.setBackgroundColor(Color.parseColor("#EEEEEE"));
            LinearLayout.LayoutParams dParams = new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 2);
            dParams.setMargins(0, 12, 0, 0);
            divider.setLayoutParams(dParams);
            item.addView(divider);

            layout.addView(item);
        }
    }

    private void renderFeatureGroups(List<PropertyDetail.FeatureGroup> groups) {
        findViewById(R.id.tvFeaturesTitle).setVisibility(View.VISIBLE);
        findViewById(R.id.layoutFeatureGroups).setVisibility(View.VISIBLE);
        findViewById(R.id.dividerFeatures).setVisibility(View.VISIBLE);

        LinearLayout layout = findViewById(R.id.layoutFeatureGroups);
        layout.removeAllViews();

        for (PropertyDetail.FeatureGroup group : groups) {
            TextView tvGroupName = new TextView(this);
            tvGroupName.setText(translate(group.getName()));
            tvGroupName.setTextSize(15);
            tvGroupName.setTypeface(null, Typeface.BOLD);
            tvGroupName.setTextColor(Color.parseColor("#333333"));
            tvGroupName.setPadding(0, 24, 0, 8);
            layout.addView(tvGroupName);

            if (group.getFeatures() != null) {
                for (PropertyDetail.Feature feature : group.getFeatures()) {
                    TextView tvFeature = new TextView(this);
                    String symbol = (feature.getSymbol() != null && !feature.getSymbol().isEmpty()) ? feature.getSymbol() : "•";
                    tvFeature.setText(symbol + " " + translate(feature.getName()));
                    tvFeature.setTextSize(14);
                    tvFeature.setTextColor(Color.parseColor("#666666"));
                    tvFeature.setPadding(16, 4, 0, 4);
                    layout.addView(tvFeature);
                }
            }
        }
    }

    private void renderNearbyPlaces(List<PropertyDetail.PlaceInfo> places) {
        findViewById(R.id.tvNearbyTitle).setVisibility(View.VISIBLE);
        findViewById(R.id.layoutNearbyPlaces).setVisibility(View.VISIBLE);

        LinearLayout layout = findViewById(R.id.layoutNearbyPlaces);
        layout.removeAllViews();

        for (PropertyDetail.PlaceInfo place : places) {
            LinearLayout row = new LinearLayout(this);
            row.setOrientation(LinearLayout.HORIZONTAL);
            row.setPadding(0, 12, 0, 12);
            row.setWeightSum(1.0f);

            TextView tvName = new TextView(this);
            tvName.setText(place.getName());
            tvName.setTextSize(14);
            tvName.setTextColor(Color.parseColor("#444444"));
            row.addView(tvName, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 0.7f));

            TextView tvDist = new TextView(this);
            tvDist.setText(place.getDistance() + " km");
            tvDist.setTextSize(14);
            tvDist.setGravity(Gravity.END);
            tvDist.setTextColor(Color.GRAY);
            row.addView(tvDist, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 0.3f));

            layout.addView(row);
        }
    }
}