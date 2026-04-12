package com.example.android_app;

import com.example.android_app.adapters.RoomAdapter;

import android.os.Bundle;
import android.widget.Toast;
import android.widget.ImageView;
import android.widget.RatingBar;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.bumptech.glide.Glide;
import com.example.android_app.models.Hotel;
import com.example.android_app.models.Room;
import com.example.android_app.network.ApiClient;
import com.example.android_app.network.ApiService;
import java.util.List;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import androidx.annotation.NonNull;

public class DetailActivity extends AppCompatActivity {

    private Hotel hotel;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_detail);

        // Lấy đối tượng Hotel được truyền từ MainActivity
        hotel = (Hotel) getIntent().getSerializableExtra("hotel_data");

        initViews();
        loadRooms();
    }

    private void initViews() {
        ImageView img = findViewById(R.id.imgHotelDetail);
        TextView name = findViewById(R.id.tvDetailName);
        RatingBar rating = findViewById(R.id.detailRatingBar);

        name.setText(hotel.getName());
        rating.setRating(hotel.getStarRating());
        Glide.with(this).load(hotel.getImageUrl()).into(img);
    }

    private void loadRooms() {
        RecyclerView rvRooms = findViewById(R.id.rvRooms);
        rvRooms.setLayoutManager(new LinearLayoutManager(this));

        ApiService apiService = ApiClient.getClient().create(ApiService.class);

        // Gọi API lấy danh sách phòng theo ID khách sạn
        apiService.getHotelRooms(hotel.getId()).enqueue(new Callback<List<Room>>() {
            @Override
            public void onResponse(@NonNull Call<List<Room>> call, @NonNull Response<List<Room>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    // DÒNG QUAN TRỌNG: Khởi tạo Adapter với dữ liệu từ Server
                    RoomAdapter adapter = new RoomAdapter(DetailActivity.this, response.body());
                    rvRooms.setAdapter(adapter);
                }
            }

            @Override
            public void onFailure(@NonNull Call<List<Room>> call, @NonNull Throwable t) {
                // Hiện thông báo lỗi nếu không kết nối được
                Toast.makeText(DetailActivity.this, "Lỗi tải phòng: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }
}