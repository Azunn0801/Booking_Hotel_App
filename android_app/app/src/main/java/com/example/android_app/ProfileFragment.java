package com.example.android_app;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.text.TextUtils;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import com.example.android_app.models.Currency;
import com.example.android_app.models.Language;
import com.example.android_app.models.LoginResponse;
import com.example.android_app.models.ProfileUpdateRequest;
import com.example.android_app.network.ApiClient;
import com.example.android_app.network.ApiService;

import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ProfileFragment extends Fragment {

    private LinearLayout layoutGuestProfile, layoutMemberProfile;
    private EditText etProfileName;
    private TextView tvProfileEmail, tvProfileLang, tvProfileCurr;
    private Button btnProfileAuth, btnUpdateProfileName, btnProfileLogout;
    private LinearLayout btnSelectLang, btnSelectCurr;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_profile, container, false);

        layoutGuestProfile = view.findViewById(R.id.layoutGuestProfile);
        layoutMemberProfile = view.findViewById(R.id.layoutMemberProfile);
        etProfileName = view.findViewById(R.id.etProfileName);
        tvProfileEmail = view.findViewById(R.id.tvProfileEmail);
        tvProfileLang = view.findViewById(R.id.tvProfileLang);
        tvProfileCurr = view.findViewById(R.id.tvProfileCurr);

        btnProfileAuth = view.findViewById(R.id.btnProfileAuth);
        btnUpdateProfileName = view.findViewById(R.id.btnUpdateProfileName);
        btnProfileLogout = view.findViewById(R.id.btnProfileLogout);

        btnSelectLang = view.findViewById(R.id.btnSelectLang);
        btnSelectCurr = view.findViewById(R.id.btnSelectCurr);

        // Listeners
        btnProfileAuth.setOnClickListener(v -> {
            Intent intent = new Intent(getActivity(), LoginActivity.class);
            startActivity(intent);
        });

        btnProfileLogout.setOnClickListener(v -> handleLogout());
        btnUpdateProfileName.setOnClickListener(v -> handleUpdateName());

        btnSelectLang.setOnClickListener(v -> loadAndShowLanguages());
        btnSelectCurr.setOnClickListener(v -> loadAndShowCurrencies());

        // Restore custom preferences
        SharedPreferences pref = requireActivity().getSharedPreferences("AgodaUserSession", Context.MODE_PRIVATE);
        tvProfileLang.setText(pref.getString("preferred_lang", "Tiếng Việt"));
        tvProfileCurr.setText(pref.getString("preferred_curr", "VND (₫)"));

        return view;
    }

    @Override
    public void onResume() {
        super.onResume();
        checkSessionAndRefresh();
    }

    private void checkSessionAndRefresh() {
        SharedPreferences pref = requireActivity().getSharedPreferences("AgodaUserSession", Context.MODE_PRIVATE);
        boolean isLoggedIn = pref.getBoolean("is_logged_in", false);

        if (!isLoggedIn) {
            layoutGuestProfile.setVisibility(View.VISIBLE);
            layoutMemberProfile.setVisibility(View.GONE);
        } else {
            layoutGuestProfile.setVisibility(View.GONE);
            layoutMemberProfile.setVisibility(View.VISIBLE);

            String name = pref.getString("full_name", "");
            String email = pref.getString("email", "");

            etProfileName.setText(name);
            tvProfileEmail.setText(email);
        }
    }

    private void handleLogout() {
        SharedPreferences pref = requireActivity().getSharedPreferences("AgodaUserSession", Context.MODE_PRIVATE);
        pref.edit().clear().apply();
        Toast.makeText(getContext(), "Đã đăng xuất!", Toast.LENGTH_SHORT).show();
        checkSessionAndRefresh();
    }

    private void handleUpdateName() {
        String newName = etProfileName.getText().toString().trim();
        if (TextUtils.isEmpty(newName)) {
            Toast.makeText(getContext(), "Tên không được để trống", Toast.LENGTH_SHORT).show();
            return;
        }

        SharedPreferences pref = requireActivity().getSharedPreferences("AgodaUserSession", Context.MODE_PRIVATE);
        int userId = pref.getInt("user_id", -1);
        if (userId == -1) return;

        ApiService apiService = ApiClient.getClient().create(ApiService.class);
        apiService.updateProfile(userId, new ProfileUpdateRequest(newName)).enqueue(new Callback<LoginResponse>() {
            @Override
            public void onResponse(@NonNull Call<LoginResponse> call, @NonNull Response<LoginResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    // Update preference
                    pref.edit().putString("full_name", response.body().getFullName()).apply();
                    Toast.makeText(getContext(), "Cập nhật tên thành công!", Toast.LENGTH_SHORT).show();
                    checkSessionAndRefresh();
                } else {
                    Toast.makeText(getContext(), "Không thể cập nhật tên!", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(@NonNull Call<LoginResponse> call, @NonNull Throwable t) {
                Toast.makeText(getContext(), "Lỗi mạng!", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void loadAndShowLanguages() {
        ApiService apiService = ApiClient.getClient().create(ApiService.class);
        apiService.getLanguages().enqueue(new Callback<List<Language>>() {
            @Override
            public void onResponse(@NonNull Call<List<Language>> call, @NonNull Response<List<Language>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    List<Language> list = response.body();
                    String[] names = new String[list.size()];
                    for (int i = 0; i < list.size(); i++) {
                        names[i] = list.get(i).getName();
                    }

                    android.app.AlertDialog.Builder builder = new android.app.AlertDialog.Builder(getContext());
                    builder.setTitle("Chọn ngôn ngữ");
                    builder.setItems(names, (dialog, which) -> {
                        String selected = names[which];
                        tvProfileLang.setText(selected);
                        SharedPreferences pref = requireActivity().getSharedPreferences("AgodaUserSession", Context.MODE_PRIVATE);
                        pref.edit().putString("preferred_lang", selected).apply();
                    });
                    builder.show();
                }
            }

            @Override
            public void onFailure(@NonNull Call<List<Language>> call, @NonNull Throwable t) {
                Toast.makeText(getContext(), "Không lấy được danh sách ngôn ngữ", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void loadAndShowCurrencies() {
        ApiService apiService = ApiClient.getClient().create(ApiService.class);
        apiService.getCurrencies().enqueue(new Callback<List<Currency>>() {
            @Override
            public void onResponse(@NonNull Call<List<Currency>> call, @NonNull Response<List<Currency>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    List<Currency> list = response.body();
                    String[] names = new String[list.size()];
                    for (int i = 0; i < list.size(); i++) {
                        names[i] = list.get(i).getName() + " (" + list.get(i).getCode() + ")";
                    }

                    android.app.AlertDialog.Builder builder = new android.app.AlertDialog.Builder(getContext());
                    builder.setTitle("Chọn tiền tệ");
                    builder.setItems(names, (dialog, which) -> {
                        String selected = names[which];
                        tvProfileCurr.setText(selected);
                        SharedPreferences pref = requireActivity().getSharedPreferences("AgodaUserSession", Context.MODE_PRIVATE);
                        pref.edit().putString("preferred_curr", selected).apply();
                    });
                    builder.show();
                }
            }

            @Override
            public void onFailure(@NonNull Call<List<Currency>> call, @NonNull Throwable t) {
                Toast.makeText(getContext(), "Không lấy được danh sách tiền tệ", Toast.LENGTH_SHORT).show();
            }
        });
    }
}
