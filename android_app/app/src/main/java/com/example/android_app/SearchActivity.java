package com.example.android_app;

import androidx.annotation.NonNull;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.app.AppCompatDelegate;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.android_app.adapters.PropertyAdapter;
import com.example.android_app.models.Property;
import com.example.android_app.network.ApiClient;
import com.example.android_app.network.ApiService;
import com.facebook.shimmer.ShimmerFrameLayout;

import java.util.ArrayList;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class SearchActivity extends AppCompatActivity {

    private ShimmerFrameLayout shimmerView;
    private RecyclerView rvHotels;
    private PropertyAdapter propertyAdapter;
    private List<Property> propertyList = new ArrayList<>();

    private ImageView btnBack;

    private String currentCityId = "1_2758";
    private String currentCityName = "Ha Noi";
    private String checkInDate = "";
    private String checkOutDate = "";
    private String currentSort = "Ranking,Desc";
    private String currentStarRating = null;
    private String currentPropertyType = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO);
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_search);

        // Get intent extras
        if (getIntent() != null) {
            currentCityId = getIntent().getStringExtra("city_id");
            currentCityName = getIntent().getStringExtra("city_name");
            checkInDate = getIntent().getStringExtra("checkin_date");
            checkOutDate = getIntent().getStringExtra("checkout_date");
            currentPropertyType = getIntent().getStringExtra("property_type");
        }

        if (currentCityId == null) currentCityId = "1_2758"; // Hà Nội (fix A9: trước đây sai là 1_1450)
        if (currentCityName == null) currentCityName = "Hà Nội";
        if (checkInDate == null) checkInDate = "";
        if (checkOutDate == null) checkOutDate = "";

        btnBack = findViewById(R.id.btnBack);
        if (btnBack != null) btnBack.setOnClickListener(v -> finish());

        View btnSort = findViewById(R.id.btnSort);
        if (btnSort != null) btnSort.setOnClickListener(v -> showSortDialog());

        View btnFilter = findViewById(R.id.btnFilter);
        if (btnFilter != null) btnFilter.setOnClickListener(v -> showFilterDialog());

        rvHotels = findViewById(R.id.rvHotels);
        shimmerView = findViewById(R.id.shimmerView);

        rvHotels.setLayoutManager(new LinearLayoutManager(this));
        propertyAdapter = new PropertyAdapter(this, propertyList, checkInDate, checkOutDate);
        rvHotels.setAdapter(propertyAdapter);

        View searchBarContainer = findViewById(R.id.searchBarContainer);
        if (searchBarContainer != null) {
            searchBarContainer.setOnClickListener(v -> showCitySelectionDialog());
        }

        updateSearchHeader();
        loadProperties();

        LinearLayout btnMap = findViewById(R.id.btnMap);
        if (btnMap != null) {
            btnMap.setOnClickListener(v -> {
                if (propertyList.isEmpty()) {
                    Toast.makeText(this, "Dang tai danh sach...", Toast.LENGTH_SHORT).show();
                    return;
                }
                MapBottomSheetFragment mapFragment = MapBottomSheetFragment.newInstance(propertyList);
                mapFragment.show(getSupportFragmentManager(), "AgodaMapWindow");
            });
        }
    }

    private void loadProperties() {
        if (shimmerView != null) {
            shimmerView.setVisibility(View.VISIBLE);
            shimmerView.startShimmer();
        }
        rvHotels.setVisibility(View.GONE);

        propertyList.clear();
        if (propertyAdapter != null) propertyAdapter.notifyDataSetChanged();

        String checkin = (checkInDate != null && !checkInDate.isEmpty()) ? checkInDate : "2026-06-01";
        String checkout = (checkOutDate != null && !checkOutDate.isEmpty()) ? checkOutDate : "2026-06-02";

        ApiService apiService = ApiClient.getClient().create(ApiService.class);
        apiService.searchProperties(
                currentCityId, checkin, checkout,
                currentPropertyType, currentStarRating,
                null, null, currentSort, 20, true
        ).enqueue(new Callback<com.example.android_app.models.SearchResponse>() {
            @Override
            public void onResponse(@NonNull Call<com.example.android_app.models.SearchResponse> call, @NonNull Response<com.example.android_app.models.SearchResponse> response) {
                if (shimmerView != null) {
                    shimmerView.stopShimmer();
                    shimmerView.setVisibility(View.GONE);
                }
                rvHotels.setVisibility(View.VISIBLE);

                if (response.isSuccessful() && response.body() != null && response.body().getProperties() != null) {
                    propertyList.addAll(response.body().getProperties());
                    propertyAdapter.notifyDataSetChanged();
                    View searchBarContainer = findViewById(R.id.searchBarContainer);
        if (searchBarContainer != null) {
            searchBarContainer.setOnClickListener(v -> showCitySelectionDialog());
        }

        updateSearchHeader();
                    // TODO: Load filter options from response.body().getFilters()
                } else {
                    Toast.makeText(SearchActivity.this, "Khong tim thay ket qua!", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(@NonNull Call<com.example.android_app.models.SearchResponse> call, @NonNull Throwable t) {
                if (shimmerView != null) {
                    shimmerView.stopShimmer();
                    shimmerView.setVisibility(View.GONE);
                }
                rvHotels.setVisibility(View.VISIBLE);
                Log.e("API_ERROR", "API call failed", t);
                Toast.makeText(SearchActivity.this, "Loi ket noi server!", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void updateSearchHeader() {
        TextView tvSearchText = findViewById(R.id.tvSearchText);
        if (tvSearchText != null) {
            StringBuilder text = new StringBuilder(currentCityName);
            if (currentPropertyType != null) {
                switch (currentPropertyType) {
                    case "hotel": text.append(" | Khach san"); break;
                    case "apartment": text.append(" | Can ho"); break;
                    case "villa": text.append(" | Villa"); break;
                }
            }
            if (checkInDate != null && !checkInDate.isEmpty() && checkOutDate != null && !checkOutDate.isEmpty()) {
                text.append(" | ").append(checkInDate).append(" -> ").append(checkOutDate);
            }
            tvSearchText.setText(text.toString());
        }
    }

    private void showSortDialog() {
        final String[] options = {"Gia thap den cao", "Gia cao den thap", "Diem danh gia cao nhat"};
        final String[] values = {"Price,Asc", "Price,Desc", "Ranking,Desc"};

        android.app.AlertDialog.Builder builder = new android.app.AlertDialog.Builder(this);
        builder.setTitle("Sap xep ket qua");
        builder.setSingleChoiceItems(options, -1, (dialog, which) -> {
            currentSort = values[which];
            loadProperties();
            dialog.dismiss();
        });
        builder.show();
    }

    private void showFilterDialog() {
        final String[] options = {"5 Sao", "4 Sao", "3 Sao"};
        final boolean[] checked = {false, false, false};
        final java.util.ArrayList<String> selected = new java.util.ArrayList<>();

        android.app.AlertDialog.Builder builder = new android.app.AlertDialog.Builder(this);
        builder.setTitle("Loc theo hang sao");
        builder.setMultiChoiceItems(options, checked, (dialog, which, isChecked) -> {
            String star = String.valueOf(5 - which);
            if (isChecked) selected.add(star);
            else selected.remove(star);
        });

        builder.setPositiveButton("Ap dung", (dialog, which) -> {
            // [FIX A10] TextUtils.join thay String.join cho tương thích API < 26
            currentStarRating = selected.isEmpty() ? null : android.text.TextUtils.join(",", selected);
            loadProperties();
        });
        builder.setNegativeButton("Huy", null);
        builder.show();
    }

    private void showCitySelectionDialog() {
        android.app.Dialog dialog = new android.app.Dialog(this);
        dialog.setContentView(R.layout.dialog_autocomplete);
        dialog.getWindow().setLayout(android.view.ViewGroup.LayoutParams.MATCH_PARENT, android.view.ViewGroup.LayoutParams.MATCH_PARENT);

        android.widget.EditText etSearch = dialog.findViewById(R.id.etSearchCity);
        android.widget.ListView lvCities = dialog.findViewById(R.id.lvCities);
        android.widget.ProgressBar pbLoading = dialog.findViewById(R.id.pbLoading);

        java.util.List<com.example.android_app.models.AutoCompleteResult> results = new java.util.ArrayList<>();
        com.example.android_app.adapters.AutocompleteAdapter autocompleteAdapter = new com.example.android_app.adapters.AutocompleteAdapter(this, results);
        lvCities.setAdapter(autocompleteAdapter);

        com.example.android_app.network.ApiService apiService = com.example.android_app.network.ApiClient.getClient().create(com.example.android_app.network.ApiService.class);

        etSearch.addTextChangedListener(new android.text.TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                if (s.length() >= 2) {
                    pbLoading.setVisibility(android.view.View.VISIBLE);
                    apiService.autocomplete(s.toString(), "vi-vn").enqueue(new retrofit2.Callback<java.util.List<com.example.android_app.models.AutoCompleteResult>>() {
                        @Override
                        public void onResponse(@androidx.annotation.NonNull retrofit2.Call<java.util.List<com.example.android_app.models.AutoCompleteResult>> call, @androidx.annotation.NonNull retrofit2.Response<java.util.List<com.example.android_app.models.AutoCompleteResult>> response) {
                            pbLoading.setVisibility(android.view.View.GONE);
                            if (response.isSuccessful() && response.body() != null) {
                                results.clear();
                                results.addAll(response.body());
                                autocompleteAdapter.notifyDataSetChanged();
                            }
                        }

                        @Override
                        public void onFailure(@androidx.annotation.NonNull retrofit2.Call<java.util.List<com.example.android_app.models.AutoCompleteResult>> call, @androidx.annotation.NonNull java.lang.Throwable t) {
                            pbLoading.setVisibility(android.view.View.GONE);
                        }
                    });
                }
            }

            @Override
            public void afterTextChanged(android.text.Editable s) {}
        });

        lvCities.setOnItemClickListener((parent, view, position, id) -> {
            com.example.android_app.models.AutoCompleteResult item = results.get(position);
            currentCityName = item.getName() != null ? item.getName() : item.getCityName();
            currentCityId = item.getSearchId();
            loadProperties();
            dialog.dismiss();
        });

        dialog.show();
    }
}
