package com.example.android_app;

import androidx.annotation.NonNull;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.TextView; // Đừng quên import TextView
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.app.AppCompatDelegate;
import androidx.constraintlayout.widget.ConstraintLayout;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.android_app.adapters.HotelAdapter;
import com.example.android_app.models.Hotel;
import com.example.android_app.network.ApiClient;
import com.example.android_app.network.ApiService;
import com.facebook.shimmer.ShimmerFrameLayout;

import java.util.ArrayList;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class MainActivity extends AppCompatActivity {

    private ShimmerFrameLayout shimmerView;
    private RecyclerView rvHotels;
    private HotelAdapter hotelAdapter;
    private List<Hotel> hotelList = new ArrayList<>();
    private boolean isLoadingMore = false;

    private LinearLayout headerContainer;
    private ConstraintLayout searchBar;

    // --- CÁC BIẾN QUẢN LÝ BỘ LỌC & TÌM KIẾM ---
    private String currentCityId = "1_318"; // Mặc định là TP.HCM
    private String currentCityName = "Tp. Hồ Chí Minh";
    private String currentSort = "Price,Asc"; // Mặc định giá thấp -> cao
    private String currentStarRating = null;  // null = lấy tất cả
    private String currentPriceRange = null;  // null = không giới hạn

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO);

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        headerContainer = findViewById(R.id.headerContainer);
        searchBar = findViewById(R.id.searchBarContainer);

        // 1. XỬ LÝ THANH TÌM KIẾM (CHỌN THÀNH PHỐ)
        if (searchBar != null) {
            searchBar.setOnClickListener(v -> showCitySelectionDialog());
        }

        // 2. XỬ LÝ NÚT SẮP XẾP (SORT)
        View btnSort = findViewById(R.id.btnSort);
        if (btnSort != null) {
            btnSort.setOnClickListener(v -> showSortDialog());
        }

        // 3. XỬ LÝ NÚT BỘ LỌC (FILTER)
        View btnFilter = findViewById(R.id.btnFilter);
        if (btnFilter != null) {
            btnFilter.setOnClickListener(v -> showFilterDialog());
        }

        // 4. Ánh xạ View
        rvHotels = findViewById(R.id.rvHotels);
        shimmerView = findViewById(R.id.shimmerView);

        // 5. Setup RecyclerView
        rvHotels.setLayoutManager(new LinearLayoutManager(this));
        hotelAdapter = new HotelAdapter(this, hotelList);
        rvHotels.setAdapter(hotelAdapter);

        // Xử lý cuộn trang (Pagination)
        rvHotels.addOnScrollListener(new RecyclerView.OnScrollListener() {
            @Override
            public void onScrolled(@NonNull RecyclerView recyclerView, int dx, int dy) {
                super.onScrolled(recyclerView, dx, dy);
                LinearLayoutManager layoutManager = (LinearLayoutManager) recyclerView.getLayoutManager();
                if (!isLoadingMore && layoutManager != null &&
                        layoutManager.findLastVisibleItemPosition() == hotelList.size() - 1) {
                    isLoadingMore = true;
                    hotelList.add(new Hotel(true));
                    hotelList.add(new Hotel(true));
                    rvHotels.post(() -> hotelAdapter.notifyItemRangeInserted(hotelList.size() - 2, 2));
                    loadMoreHotels();
                }
            }
        });

        // 6. Bắt đầu hiệu ứng lấp lánh
        if (shimmerView != null) {
            shimmerView.startShimmer();
        }

        // 7. Gọi API lần đầu
        loadHotels();

        // 8. Xử lý nút Bản đồ
        LinearLayout btnMap = findViewById(R.id.btnMap);
        if (btnMap != null) {
            btnMap.setOnClickListener(v -> {
                if (hotelList == null || hotelList.isEmpty()) {
                    Toast.makeText(this, "Đang tải danh sách khách sạn...", Toast.LENGTH_SHORT).show();
                    return;
                }
                MapBottomSheetFragment mapFragment = MapBottomSheetFragment.newInstance(hotelList);
                mapFragment.show(getSupportFragmentManager(), "AgodaMapWindow");
            });
        }

        // 9. Xử lý nút Yêu thích
        LinearLayout btnWishlist = findViewById(R.id.btnWishlist);
        if (btnWishlist != null) {
            btnWishlist.setOnClickListener(v -> {
                Toast.makeText(this, "Tính năng đang phát triển", Toast.LENGTH_SHORT).show();
            });
        }
    }

    private void loadHotels() {
        if (shimmerView != null) {
            shimmerView.setVisibility(View.VISIBLE);
            shimmerView.startShimmer();
        }
        rvHotels.setVisibility(View.GONE);

        hotelList.clear();
        if (hotelAdapter != null) hotelAdapter.notifyDataSetChanged();

        ApiService apiService = ApiClient.getClient().create(ApiService.class);

        // GỌI API VỚI THAM SỐ ĐỘNG
        Call<List<Hotel>> call = apiService.searchHotels(
                currentCityId,
                currentStarRating,
                currentPriceRange,
                currentSort
        );

        call.enqueue(new Callback<List<Hotel>>() {
            @Override
            public void onResponse(@NonNull Call<List<Hotel>> call, @NonNull Response<List<Hotel>> response) {
                if (shimmerView != null) {
                    shimmerView.stopShimmer();
                    shimmerView.setVisibility(View.GONE);
                }
                rvHotels.setVisibility(View.VISIBLE);

                if (response.isSuccessful() && response.body() != null) {
                    hotelList.addAll(response.body());
                    hotelAdapter.notifyDataSetChanged();
                    updateSearchText(); // Cập nhật tên thành phố
                } else {
                    Toast.makeText(MainActivity.this, "Không tìm thấy khách sạn nào!", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(@NonNull Call<List<Hotel>> call, @NonNull Throwable t) {
                if (shimmerView != null) {
                    shimmerView.stopShimmer();
                    shimmerView.setVisibility(View.GONE);
                }
                Log.e("API_ERROR", t.getMessage());
                Toast.makeText(MainActivity.this, "Lỗi kết nối server!", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void updateSearchText() {
        // Tìm TextView hiển thị tên thành phố
        TextView tvSearchText = findViewById(R.id.tvSearchText);
        if (tvSearchText != null) {
            tvSearchText.setText(currentCityName);
        }
    }

    private void loadMoreHotels() {
        ApiService apiService = ApiClient.getClient().create(ApiService.class);
        // Lưu ý: loadMore cũng nên dùng tham số động giống loadHotels
        Call<List<Hotel>> call = apiService.searchHotels(currentCityId, currentStarRating, currentPriceRange, currentSort);

        call.enqueue(new Callback<List<Hotel>>() {
            @Override
            public void onResponse(@NonNull Call<List<Hotel>> call, @NonNull Response<List<Hotel>> response) {
                removeLoadingItems();
                isLoadingMore = false;

                if (response.isSuccessful() && response.body() != null) {
                    int startPos = hotelList.size();
                    hotelList.addAll(response.body());
                    hotelAdapter.notifyItemRangeInserted(startPos, response.body().size());
                }
            }

            @Override
            public void onFailure(@NonNull Call<List<Hotel>> call, @NonNull Throwable t) {
                removeLoadingItems();
                isLoadingMore = false;
                Toast.makeText(MainActivity.this, "Lỗi khi tải thêm dữ liệu!", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void removeLoadingItems() {
        if (hotelList.size() >= 2) {
            hotelList.remove(hotelList.size() - 1);
            hotelList.remove(hotelList.size() - 1);
            hotelAdapter.notifyItemRangeRemoved(hotelList.size(), 2);
        }
    }

    // --- CÁC HÀM DIALOG (BẮT BUỘC PHẢI NẰM TRONG CLASS MainActivity) ---

    private void showCitySelectionDialog() {
        final String[] cities = {"TP. Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Vũng Tàu", "Đà Lạt", "Nha Trang"};
        final String[] ids = {"1_318", "1_2758", "1_16552", "1_17215", "1_15932", "1_16207"};

        android.app.AlertDialog.Builder builder = new android.app.AlertDialog.Builder(this);
        builder.setTitle("Bạn muốn đi đâu?");
        builder.setItems(cities, (dialog, which) -> {
            currentCityName = cities[which];
            currentCityId = ids[which];
            loadHotels();
        });
        builder.show();
    }

    private void showSortDialog() {
        final String[] options = {"Giá thấp đến cao", "Giá cao đến thấp", "Điểm đánh giá cao nhất"};
        final String[] values = {"Price,Asc", "Price,Desc", "Score,Desc"};

        android.app.AlertDialog.Builder builder = new android.app.AlertDialog.Builder(this);
        builder.setTitle("Sắp xếp kết quả");
        builder.setSingleChoiceItems(options, -1, (dialog, which) -> {
            currentSort = values[which];
            loadHotels();
            dialog.dismiss();
        });
        builder.show();
    }

    private void showFilterDialog() {
        final String[] options = {"5 Sao", "4 Sao", "3 Sao"};
        final boolean[] checked = {false, false, false};
        final java.util.ArrayList<String> selected = new java.util.ArrayList<>();

        android.app.AlertDialog.Builder builder = new android.app.AlertDialog.Builder(this);
        builder.setTitle("Lọc theo hạng sao");
        builder.setMultiChoiceItems(options, checked, (dialog, which, isChecked) -> {
            String star = String.valueOf(5 - which);
            if (isChecked) selected.add(star);
            else selected.remove(star);
        });

        builder.setPositiveButton("Áp dụng", (dialog, which) -> {
            if (!selected.isEmpty()) {
                currentStarRating = String.join(",", selected);
            } else {
                currentStarRating = null;
            }
            loadHotels();
        });
        builder.setNegativeButton("Hủy", null);
        builder.show();
    }

} // <--- DẤU NGOẶC KẾT THÚC CLASS PHẢI NẰM Ở CUỐI CÙNG
