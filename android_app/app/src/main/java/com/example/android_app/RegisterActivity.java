package com.example.android_app;

import android.content.Intent;
import android.os.Bundle;
import android.text.TextUtils;
import android.util.Patterns;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.example.android_app.models.UserCreateRequest;
import com.example.android_app.network.ApiClient;
import com.example.android_app.network.ApiService;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class RegisterActivity extends AppCompatActivity {

    private EditText etFullName, etEmail, etPassword, etConfirmPassword;
    private Button btnRegister;
    private TextView tvLoginLink;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_register);

        etFullName = findViewById(R.id.etFullName);
        etEmail = findViewById(R.id.etEmail);
        etPassword = findViewById(R.id.etPassword);
        etConfirmPassword = findViewById(R.id.etConfirmPassword);
        btnRegister = findViewById(R.id.btnRegister);
        tvLoginLink = findViewById(R.id.tvLoginLink);

        btnRegister.setOnClickListener(v -> handleRegister());
        tvLoginLink.setOnClickListener(v -> finish());
    }

    private void handleRegister() {
        String fullName = etFullName.getText().toString().trim();
        String email = etEmail.getText().toString().trim();
        String password = etPassword.getText().toString().trim();
        // Confirm password chỉ validate nếu view tồn tại trong layout
        String confirmPassword = (etConfirmPassword != null)
                ? etConfirmPassword.getText().toString().trim()
                : password;

        // Validate họ tên
        if (TextUtils.isEmpty(fullName)) {
            etFullName.setError("Vui lòng nhập họ tên");
            etFullName.requestFocus();
            return;
        }

        // Validate email format
        if (TextUtils.isEmpty(email)) {
            etEmail.setError("Vui lòng nhập email");
            etEmail.requestFocus();
            return;
        }
        if (!Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
            etEmail.setError("Email không hợp lệ");
            etEmail.requestFocus();
            return;
        }

        // Validate password
        if (TextUtils.isEmpty(password)) {
            etPassword.setError("Vui lòng nhập mật khẩu");
            etPassword.requestFocus();
            return;
        }
        if (password.length() < 6) {
            etPassword.setError("Mật khẩu phải có ít nhất 6 ký tự");
            etPassword.requestFocus();
            return;
        }

        // Validate confirm password nếu có
        if (etConfirmPassword != null && !TextUtils.isEmpty(confirmPassword)
                && !password.equals(confirmPassword)) {
            etConfirmPassword.setError("Mật khẩu xác nhận không khớp");
            etConfirmPassword.requestFocus();
            return;
        }

        // Loading state
        btnRegister.setEnabled(false);
        btnRegister.setText("Đang đăng ký...");

        UserCreateRequest request = new UserCreateRequest(email, password, fullName);
        ApiService apiService = ApiClient.getClient().create(ApiService.class);
        apiService.registerUser(request).enqueue(new Callback<Void>() {
            @Override
            public void onResponse(@NonNull Call<Void> call, @NonNull Response<Void> response) {
                btnRegister.setEnabled(true);
                btnRegister.setText("Đăng ký");
                if (response.isSuccessful()) {
                    Toast.makeText(RegisterActivity.this,
                            "Đăng ký thành công! Vui lòng đăng nhập", Toast.LENGTH_LONG).show();
                    // Chuyển về LoginActivity, prefill email
                    Intent intent = new Intent(RegisterActivity.this, LoginActivity.class);
                    intent.putExtra("prefill_email", email);
                    intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);
                    startActivity(intent);
                    finish();
                } else {
                    if (response.code() == 400) {
                        Toast.makeText(RegisterActivity.this,
                                "Email này đã được đăng ký!", Toast.LENGTH_SHORT).show();
                    } else {
                        Toast.makeText(RegisterActivity.this,
                                "Đăng ký thất bại! Vui lòng thử lại.", Toast.LENGTH_SHORT).show();
                    }
                }
            }

            @Override
            public void onFailure(@NonNull Call<Void> call, @NonNull Throwable t) {
                btnRegister.setEnabled(true);
                btnRegister.setText("Đăng ký");
                Toast.makeText(RegisterActivity.this, "Lỗi kết nối máy chủ!", Toast.LENGTH_SHORT).show();
            }
        });
    }
}
