package com.example.android_app;

import com.example.android_app.adapters.RoomAdapter;

import android.os.Bundle;
import android.util.Log;
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
import java.util.List;
import java.util.ArrayList;

public class DetailActivity extends AppCompatActivity {
    private RecyclerView rvRooms;
    private RoomAdapter roomAdapter;
    private List<Room> roomList = new ArrayList<>();
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

        // Đảm bảo ID rvRooms khớp với file activity_detail.xml của bạn
        rvRooms = findViewById(R.id.rvRooms);
        rvRooms.setLayoutManager(new LinearLayoutManager(this));

        // Khởi tạo Adapter và gán cho RecyclerView
        roomAdapter = new RoomAdapter(this, roomList);
        rvRooms.setAdapter(roomAdapter);
    }

    private void loadRooms() {
        if (hotel != null && hotel.getId() != null) {
            int hotelId = Integer.parseInt(hotel.getId());

            // LƯU Ý: Đổi 'apiService' thành biến hoặc class gọi API thực tế của bạn
            // (Ví dụ: ApiClient.getApiService().getRoomPrices...)
            ApiClient.getClient().create(ApiService.class).getRoomPrices(hotelId).enqueue(new Callback<List<Room>>() {
                @Override
                public void onResponse(Call<List<Room>> call, Response<List<Room>> response) {
                    if (response.isSuccessful() && response.body() != null) {
                        roomList.clear();
                        roomList.addAll(response.body());
                        roomAdapter.notifyDataSetChanged(); // Cập nhật giao diện
                    }
                }

                @Override
                public void onFailure(Call<List<Room>> call, Throwable t) {
                    Log.e("API_ERROR", "Không lấy được danh sách phòng: " + t.getMessage());
                }
            });
        }
    }
}