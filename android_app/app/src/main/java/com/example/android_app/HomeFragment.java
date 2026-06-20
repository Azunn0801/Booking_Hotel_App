package com.example.android_app;

import android.app.DatePickerDialog;
import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.android_app.adapters.PropertyAdapter;
import com.example.android_app.adapters.AutocompleteAdapter;
import com.example.android_app.models.AutoCompleteResult;
import com.example.android_app.models.Property;
import com.example.android_app.network.ApiClient;
import com.example.android_app.network.ApiService;
import com.facebook.shimmer.ShimmerFrameLayout;
import android.text.Editable;
import android.text.TextWatcher;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.app.Dialog;


import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;
import java.util.Locale;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class HomeFragment extends Fragment {

    private TextView tvHomeCity, tvCheckInDate, tvCheckOutDate;
    private LinearLayout btnSelectCity, btnCheckInDate, btnCheckOutDate;
    private Button btnHomeSearch;
    private ShimmerFrameLayout shimmerNearby;
    private RecyclerView rvNearby;


    private PropertyAdapter adapter;
    private List<Property> recommendedProperties = new ArrayList<>();

    private String currentCityId = "1_13170"; // [FIX] Mặc định là Hồ Chí Minh
    private String currentCityName = "Hồ Chí Minh";
    private Calendar checkInCal, checkOutCal;
    private SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd", Locale.US);
    private String currentPropertyType = null; // null = all, "hotel", "apartment", "villa"

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_home, container, false);

        tvHomeCity = view.findViewById(R.id.tvHomeCity);
        tvCheckInDate = view.findViewById(R.id.tvCheckInDate);
        tvCheckOutDate = view.findViewById(R.id.tvCheckOutDate);
        btnSelectCity = view.findViewById(R.id.btnSelectCity);
        btnCheckInDate = view.findViewById(R.id.btnCheckInDate);
        btnCheckOutDate = view.findViewById(R.id.btnCheckOutDate);
        btnHomeSearch = view.findViewById(R.id.btnHomeSearch);
        shimmerNearby = view.findViewById(R.id.shimmerNearby);
        rvNearby = view.findViewById(R.id.rvNearby);
        // Date init
        checkInCal = Calendar.getInstance();
        checkOutCal = Calendar.getInstance();
        checkOutCal.add(Calendar.DAY_OF_YEAR, 1);
        tvCheckInDate.setText(dateFormat.format(checkInCal.getTime()));
        tvCheckOutDate.setText(dateFormat.format(checkOutCal.getTime()));

        // RecyclerView — [FIX A11] truyền dates vào adapter thay vì null
        rvNearby.setLayoutManager(new LinearLayoutManager(requireContext()));
        adapter = new PropertyAdapter(requireContext(), recommendedProperties,
                dateFormat.format(checkInCal.getTime()),
                dateFormat.format(checkOutCal.getTime()));
        rvNearby.setAdapter(adapter);

        // Actions
        btnSelectCity.setOnClickListener(v -> showCitySelectionDialog());
        btnCheckInDate.setOnClickListener(v -> showDatePicker(true));
        btnCheckOutDate.setOnClickListener(v -> showDatePicker(false));

        btnHomeSearch.setOnClickListener(v -> {
            Intent intent = new Intent(getActivity(), SearchActivity.class);
            intent.putExtra("city_id", currentCityId);
            intent.putExtra("city_name", currentCityName);
            intent.putExtra("checkin_date", tvCheckInDate.getText().toString());
            intent.putExtra("checkout_date", tvCheckOutDate.getText().toString());
            intent.putExtra("property_type", currentPropertyType);
            startActivity(intent);
        });

        TextView tabHotels = view.findViewById(R.id.tabHotels);
        TextView tabVillas = view.findViewById(R.id.tabVillas);
        TextView tabResorts = view.findViewById(R.id.tabResorts);
        TextView tabApartments = view.findViewById(R.id.tabApartments);

        if (tabHotels != null) {
            tabHotels.setOnClickListener(v -> {
                currentPropertyType = "hotel";
                selectTab(view, tabHotels);
                loadRecommendedProperties();
            });
        }
        if (tabVillas != null) {
            tabVillas.setOnClickListener(v -> {
                currentPropertyType = "villa";
                selectTab(view, tabVillas);
                loadRecommendedProperties();
            });
        }
        if (tabResorts != null) {
            tabResorts.setOnClickListener(v -> {
                currentPropertyType = "resort";
                selectTab(view, tabResorts);
                loadRecommendedProperties();
            });
        }
        if (tabApartments != null) {
            tabApartments.setOnClickListener(v -> {
                currentPropertyType = "apartment";
                selectTab(view, tabApartments);
                loadRecommendedProperties();
            });
        }

        loadRecommendedProperties();
        return view;
    }

    private void showDatePicker(boolean isCheckIn) {
        Calendar cal = isCheckIn ? checkInCal : checkOutCal;
        DatePickerDialog datePickerDialog = new DatePickerDialog(requireContext(),
                (view, year, month, dayOfMonth) -> {
                    cal.set(Calendar.YEAR, year);
                    cal.set(Calendar.MONTH, month);
                    cal.set(Calendar.DAY_OF_MONTH, dayOfMonth);

                    if (isCheckIn) {
                        tvCheckInDate.setText(dateFormat.format(cal.getTime()));
                        if (checkOutCal.before(checkInCal) || checkOutCal.equals(checkInCal)) {
                            checkOutCal.setTime(checkInCal.getTime());
                            checkOutCal.add(Calendar.DAY_OF_YEAR, 1);
                            tvCheckOutDate.setText(dateFormat.format(checkOutCal.getTime()));
                        }
                    } else {
                        if (cal.before(checkInCal) || cal.equals(checkInCal)) {
                            Toast.makeText(requireContext(), "Ngay tra phong phai sau ngay nhan phong!", Toast.LENGTH_SHORT).show();
                        } else {
                            tvCheckOutDate.setText(dateFormat.format(cal.getTime()));
                        }
                    }
                },
                cal.get(Calendar.YEAR), cal.get(Calendar.MONTH), cal.get(Calendar.DAY_OF_MONTH));

        datePickerDialog.getDatePicker().setMinDate(System.currentTimeMillis() - 1000);
        datePickerDialog.show();
    }

    private void showCitySelectionDialog() {
        Dialog dialog = new Dialog(requireContext());
        dialog.setContentView(R.layout.dialog_autocomplete);
        dialog.getWindow().setLayout(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT);

        EditText etSearch = dialog.findViewById(R.id.etSearchCity);
        ListView lvCities = dialog.findViewById(R.id.lvCities);
        ProgressBar pbLoading = dialog.findViewById(R.id.pbLoading);

        List<AutoCompleteResult> results = new ArrayList<>();
        AutocompleteAdapter autocompleteAdapter = new AutocompleteAdapter(requireContext(), results);
        lvCities.setAdapter(autocompleteAdapter);

        ApiService apiService = ApiClient.getClient().create(ApiService.class);

        etSearch.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                if (s.length() >= 2) {
                    pbLoading.setVisibility(View.VISIBLE);
                    apiService.autocomplete(s.toString(), "vi-vn").enqueue(new Callback<List<AutoCompleteResult>>() {
                        @Override
                        public void onResponse(@NonNull Call<List<AutoCompleteResult>> call, @NonNull Response<List<AutoCompleteResult>> response) {
                            pbLoading.setVisibility(View.GONE);
                            if (response.isSuccessful() && response.body() != null) {
                                results.clear();
                                results.addAll(response.body());
                                autocompleteAdapter.notifyDataSetChanged();
                            }
                        }

                        @Override
                        public void onFailure(@NonNull Call<List<AutoCompleteResult>> call, @NonNull Throwable t) {
                            pbLoading.setVisibility(View.GONE);
                        }
                    });
                }
            }

            @Override
            public void afterTextChanged(Editable s) {}
        });

        lvCities.setOnItemClickListener((parent, view, position, id) -> {
            AutoCompleteResult item = results.get(position);
            currentCityName = item.getName() != null ? item.getName() : item.getCityName();
            currentCityId = item.getSearchId();
            tvHomeCity.setText(currentCityName);
            loadRecommendedProperties();
            dialog.dismiss();
        });

        dialog.show();
    }

    private void selectTab(View view, TextView selectedTab) {
        TextView t1 = view.findViewById(R.id.tabHotels);
        TextView t2 = view.findViewById(R.id.tabVillas);
        TextView t3 = view.findViewById(R.id.tabResorts);
        TextView t4 = view.findViewById(R.id.tabApartments);
        
        TextView[] tabs = {t1, t2, t3, t4};
        for (TextView tab : tabs) {
            if (tab != null) {
                if (tab == selectedTab) {
                    tab.setTextColor(0xFF0073BB);
                    tab.setBackgroundResource(R.drawable.bg_circle_white);
                    tab.setTypeface(null, android.graphics.Typeface.BOLD);
                } else {
                    tab.setTextColor(0xFF888888);
                    tab.setBackground(null);
                    tab.setTypeface(null, android.graphics.Typeface.NORMAL);
                }
            }
        }
    }

    private void loadRecommendedProperties() {
        if (shimmerNearby != null) {
            shimmerNearby.setVisibility(View.VISIBLE);
            shimmerNearby.startShimmer();
        }
        rvNearby.setVisibility(View.GONE);

        String checkin = dateFormat.format(checkInCal.getTime());
        String checkout = dateFormat.format(checkOutCal.getTime());

        ApiService apiService = ApiClient.getClient().create(ApiService.class);
        apiService.searchProperties(
                currentCityId, checkin, checkout,
                currentPropertyType, null, null, null,
                "Ranking,Desc", 10, true
        ).enqueue(new Callback<com.example.android_app.models.SearchResponse>() {
            @Override
            public void onResponse(@NonNull Call<com.example.android_app.models.SearchResponse> call, @NonNull Response<com.example.android_app.models.SearchResponse> response) {
                if (shimmerNearby != null) {
                    shimmerNearby.stopShimmer();
                    shimmerNearby.setVisibility(View.GONE);
                }
                rvNearby.setVisibility(View.VISIBLE);

                if (response.isSuccessful() && response.body() != null && response.body().getProperties() != null) {
                    recommendedProperties.clear();
                    recommendedProperties.addAll(response.body().getProperties());
                    adapter.notifyDataSetChanged();
                }
            }

            @Override
            public void onFailure(@NonNull Call<com.example.android_app.models.SearchResponse> call, @NonNull Throwable t) {
                if (shimmerNearby != null) {
                    shimmerNearby.stopShimmer();
                    shimmerNearby.setVisibility(View.GONE);
                }
                rvNearby.setVisibility(View.VISIBLE);
                Toast.makeText(requireContext(), "Khong the tai du lieu", Toast.LENGTH_SHORT).show();
            }
        });
    }
}
