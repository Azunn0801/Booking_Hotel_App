package com.example.android_app;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.android_app.adapters.BookingAdapter;
import com.example.android_app.models.BookingResponse;
import com.example.android_app.network.ApiClient;
import com.example.android_app.network.ApiService;

import java.util.ArrayList;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class BookingsFragment extends Fragment {

    private LinearLayout layoutAuthPrompt, layoutEmptyBookings;
    private RecyclerView rvBookings;
    private Button btnBookingsLogin;
    private List<BookingResponse> bookingList = new ArrayList<>();
    private BookingAdapter adapter;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_bookings, container, false);

        layoutAuthPrompt = view.findViewById(R.id.layoutAuthPrompt);
        layoutEmptyBookings = view.findViewById(R.id.layoutEmptyBookings);
        rvBookings = view.findViewById(R.id.rvBookings);
        btnBookingsLogin = view.findViewById(R.id.btnBookingsLogin);

        rvBookings.setLayoutManager(new LinearLayoutManager(getContext()));
        adapter = new BookingAdapter(getContext(), bookingList);
        rvBookings.setAdapter(adapter);

        btnBookingsLogin.setOnClickListener(v -> {
            Intent intent = new Intent(getActivity(), LoginActivity.class);
            startActivity(intent);
        });

        return view;
    }

    @Override
    public void onResume() {
        super.onResume();
        checkSessionAndLoad();
    }

    private void checkSessionAndLoad() {
        SharedPreferences pref = requireActivity().getSharedPreferences("AgodaUserSession", Context.MODE_PRIVATE);
        boolean isLoggedIn = pref.getBoolean("is_logged_in", false);

        if (!isLoggedIn) {
            layoutAuthPrompt.setVisibility(View.VISIBLE);
            layoutEmptyBookings.setVisibility(View.GONE);
            rvBookings.setVisibility(View.GONE);
        } else {
            layoutAuthPrompt.setVisibility(View.GONE);
            int userId = pref.getInt("user_id", -1);
            loadBookings(userId);
        }
    }

    private void loadBookings(int userId) {
        ApiService apiService = ApiClient.getClient().create(ApiService.class);
        apiService.getUserBookings(userId).enqueue(new Callback<List<BookingResponse>>() {
            @Override
            public void onResponse(@NonNull Call<List<BookingResponse>> call, @NonNull Response<List<BookingResponse>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    bookingList.clear();
                    bookingList.addAll(response.body());
                    adapter.notifyDataSetChanged();

                    if (bookingList.isEmpty()) {
                        layoutEmptyBookings.setVisibility(View.VISIBLE);
                        rvBookings.setVisibility(View.GONE);
                    } else {
                        layoutEmptyBookings.setVisibility(View.GONE);
                        rvBookings.setVisibility(View.VISIBLE);
                    }
                } else {
                    layoutEmptyBookings.setVisibility(View.VISIBLE);
                    rvBookings.setVisibility(View.GONE);
                }
            }

            @Override
            public void onFailure(@NonNull Call<List<BookingResponse>> call, @NonNull Throwable t) {
                Toast.makeText(getContext(), "Không thể tải lịch sử đặt dịch vụ", Toast.LENGTH_SHORT).show();
            }
        });
    }
}
