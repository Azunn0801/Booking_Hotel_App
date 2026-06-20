package com.example.android_app;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.text.TextUtils;
import android.util.Patterns;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.example.android_app.models.BookingRequest;
import com.example.android_app.models.BookingResponse;
import com.example.android_app.models.Property;
import com.example.android_app.models.PromoApplyRequest;
import com.example.android_app.models.PromoApplyResponse;
import com.example.android_app.models.Room;
import com.example.android_app.network.ApiClient;
import com.example.android_app.network.ApiService;

import java.text.SimpleDateFormat;
import java.util.Locale;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class CheckoutActivity extends AppCompatActivity {

    private TextView tvPropertyName, tvPropertyAddress, tvRoomName, tvAmenities, tvBasePrice, tvTotalPrice;
    private TextView tvDiscountLabel, tvDiscountAmount;
    private EditText etName, etEmail, etPhone, etPromoCode;
    private Button btnConfirm, btnApplyPromo;
    private LinearLayout layoutPromoResult;

    private Property property;
    private Room room;
    private int userId = -1;
    private String checkInDate;
    private String checkOutDate;
    private double currentDiscount = 0;
    private String appliedPromoCode = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_checkout);

        // Session check
        SharedPreferences pref = getSharedPreferences("AgodaUserSession", MODE_PRIVATE);
        boolean isLoggedIn = pref.getBoolean("is_logged_in", false);
        if (!isLoggedIn) {
            Toast.makeText(this, "Vui long dang nhap de thuc hien dat phong!", Toast.LENGTH_LONG).show();
            startActivity(new Intent(this, LoginActivity.class));
            finish();
            return;
        }

        userId = pref.getInt("user_id", -1);
        property = (Property) getIntent().getSerializableExtra("property_data");
        room = (Room) getIntent().getSerializableExtra("room_data");
        checkInDate = getIntent().getStringExtra("checkin_date");
        checkOutDate = getIntent().getStringExtra("checkout_date");

        if (property == null || room == null) {
            Toast.makeText(this, "Khong co du lieu dat phong hop le!", Toast.LENGTH_SHORT).show();
            finish();
            return;
        }

        // Bind views
        tvPropertyName = findViewById(R.id.tvCheckoutHotelName);
        tvPropertyAddress = findViewById(R.id.tvCheckoutHotelAddress);
        tvRoomName = findViewById(R.id.tvCheckoutRoomName);
        tvAmenities = findViewById(R.id.tvCheckoutAmenities);
        tvBasePrice = findViewById(R.id.tvCheckoutBasePrice);
        tvTotalPrice = findViewById(R.id.tvCheckoutTotalPrice);
        tvDiscountLabel = findViewById(R.id.tvCheckoutDiscountLabel);
        tvDiscountAmount = findViewById(R.id.tvCheckoutDiscountAmount);
        etName = findViewById(R.id.etCheckoutName);
        etEmail = findViewById(R.id.etCheckoutEmail);
        etPhone = findViewById(R.id.etCheckoutPhone);
        etPromoCode = findViewById(R.id.etPromoCode);
        btnConfirm = findViewById(R.id.btnCheckoutConfirm);
        btnApplyPromo = findViewById(R.id.btnApplyPromo);
        // [FIX A4] Bind layoutPromoResult — trước đây bị khai báo nhưng không bao giờ gán
        layoutPromoResult = findViewById(R.id.layoutPromoResult);

        // Pre-fill
        etName.setText(pref.getString("full_name", ""));
        etEmail.setText(pref.getString("email", ""));

        // Setup values
        tvPropertyName.setText(property.getName());
        tvPropertyAddress.setText(property.getAddress());
        tvRoomName.setText(room.getRoomName());
        tvAmenities.setText("Tien nghi: " + room.getAmenities());

        // Calculate nights
        final int totalNights = Math.max(calculateNights(checkInDate, checkOutDate), 1);

        double pricePerNight = room.getPrice();
        double totalPrice = pricePerNight * totalNights;

        tvBasePrice.setText(String.format(Locale.US, "%,.0f VND/đem", pricePerNight));
        updateTotalPrice(totalPrice, totalNights);

        // Promo code
        btnApplyPromo.setOnClickListener(v -> applyPromoCode(totalPrice));

        btnConfirm.setOnClickListener(v -> handleConfirmBooking(totalNights));
    }

    private void applyPromoCode(double originalTotal) {
        String code = etPromoCode.getText().toString().trim();
        if (TextUtils.isEmpty(code)) {
            Toast.makeText(this, "Vui long nhap ma khuyen mai", Toast.LENGTH_SHORT).show();
            return;
        }

        ApiService apiService = ApiClient.getClient().create(ApiService.class);
        apiService.applyPromotion(new PromoApplyRequest(code, originalTotal)).enqueue(new Callback<PromoApplyResponse>() {
            @Override
            public void onResponse(@NonNull Call<PromoApplyResponse> call, @NonNull Response<PromoApplyResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    PromoApplyResponse result = response.body();
                    currentDiscount = result.getDiscountAmount();
                    appliedPromoCode = result.getCode();

                    if (tvDiscountLabel != null) tvDiscountLabel.setVisibility(View.VISIBLE);
                    if (tvDiscountAmount != null) {
                        tvDiscountAmount.setVisibility(View.VISIBLE);
                        tvDiscountAmount.setText("-" + String.format(Locale.US, "%,.0f VND", currentDiscount));
                    }

                    int nights = calculateNights(checkInDate, checkOutDate);
                    if (nights < 1) nights = 1;
                    double finalPrice = room.getPrice() * nights - currentDiscount;
                    if (finalPrice < 0) finalPrice = 0;
                    updateTotalPrice(finalPrice, nights);

                    Toast.makeText(CheckoutActivity.this,
                            "Ap dung ma " + result.getTitle() + " thanh cong! Giam " +
                                    String.format(Locale.US, "%,.0f VND", currentDiscount),
                            Toast.LENGTH_LONG).show();
                } else {
                    Toast.makeText(CheckoutActivity.this, "Ma khuyen mai khong hop le!", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(@NonNull Call<PromoApplyResponse> call, @NonNull Throwable t) {
                Toast.makeText(CheckoutActivity.this, "Loi ket noi may chu!", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void updateTotalPrice(double totalPrice, int nights) {
        if (tvTotalPrice != null) {
            tvTotalPrice.setText(String.format(Locale.US, "%,.0f VND (%d dem)", totalPrice, nights));
        }
    }

    private void handleConfirmBooking(int nights) {
        String name = etName.getText().toString().trim();
        String email = etEmail.getText().toString().trim();
        String phone = etPhone.getText().toString().trim();

        if (TextUtils.isEmpty(name) || TextUtils.isEmpty(email) || TextUtils.isEmpty(phone)) {
            Toast.makeText(this, "Vui lòng nhập đầy đủ họ tên, email và số điện thoại", Toast.LENGTH_SHORT).show();
            return;
        }

        // [FIX A5] Validate email format
        if (!Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
            etEmail.setError("Email không hợp lệ");
            etEmail.requestFocus();
            return;
        }

        String checkin = (checkInDate != null && !checkInDate.isEmpty()) ? checkInDate :
                new SimpleDateFormat("yyyy-MM-dd", Locale.US).format(new java.util.Date());
        String checkout = (checkOutDate != null && !checkOutDate.isEmpty()) ? checkOutDate :
                new SimpleDateFormat("yyyy-MM-dd", Locale.US).format(new java.util.Date());

        if (nights < 1) nights = 1;
        // [FIX A6] originalTotal là giá gốc TRƯỚC khi giảm, không phụ thuộc vào promo
        double originalTotal = room.getPrice() * nights;
        // finalTotal = originalTotal trừ discount đã áp dụng từ server
        double finalTotal = Math.max(originalTotal - currentDiscount, 0);
        if (finalTotal < 0) finalTotal = 0;

        BookingRequest bookingRequest = new BookingRequest(
                userId,
                property.getId(),
                property.getName(),
                property.getPropertyType(),
                property.getImageUrl(),
                checkin,
                checkout,
                finalTotal,
                originalTotal,
                currentDiscount,
                appliedPromoCode
        );

        ApiService apiService = ApiClient.getClient().create(ApiService.class);
        apiService.createBooking(bookingRequest).enqueue(new Callback<BookingResponse>() {
            @Override
            public void onResponse(@NonNull Call<BookingResponse> call, @NonNull Response<BookingResponse> response) {
                if (response.isSuccessful()) {
                    Toast.makeText(CheckoutActivity.this, "Dat phong thanh cong!", Toast.LENGTH_LONG).show();
                    Intent intent = new Intent(CheckoutActivity.this, MainActivity.class);
                    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
                    intent.putExtra("open_tab", "bookings");
                    startActivity(intent);
                    finish();
                } else {
                    Toast.makeText(CheckoutActivity.this, "Dat phong that bai. Vui long thu lai!", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(@NonNull Call<BookingResponse> call, @NonNull Throwable t) {
                Toast.makeText(CheckoutActivity.this, "Loi ket noi may chu!", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private int calculateNights(String checkinStr, String checkoutStr) {
        if (checkinStr == null || checkoutStr == null || checkinStr.isEmpty() || checkoutStr.isEmpty()) {
            return 1;
        }
        try {
            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd", Locale.US);
            java.util.Date ci = sdf.parse(checkinStr);
            java.util.Date co = sdf.parse(checkoutStr);
            if (ci != null && co != null) {
                long diffMs = co.getTime() - ci.getTime();
                long diffDays = diffMs / (1000 * 60 * 60 * 24);
                return (int) Math.max(diffDays, 1);
            }
        } catch (Exception e) {
            // fallback
        }
        return 1;
    }
}
