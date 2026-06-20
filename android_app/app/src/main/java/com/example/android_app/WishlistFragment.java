package com.example.android_app;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.android_app.adapters.PropertyAdapter;
import com.example.android_app.models.Property;
import com.google.gson.Gson;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;
import java.util.Locale;
import java.util.Map;

public class WishlistFragment extends Fragment {

    private LinearLayout layoutEmptyWishlist;
    private RecyclerView rvWishlist;
    private List<Property> wishlist = new ArrayList<>();
    private PropertyAdapter adapter;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_wishlist, container, false);

        layoutEmptyWishlist = view.findViewById(R.id.layoutEmptyWishlist);
        rvWishlist = view.findViewById(R.id.rvWishlist);

        rvWishlist.setLayoutManager(new LinearLayoutManager(requireContext()));
        // [FIX A13] Truyền ngày mặc định vào adapter — trước đây null khiến checkout không có ngày
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd", Locale.US);
        Calendar cal = Calendar.getInstance();
        cal.add(Calendar.DAY_OF_YEAR, 1);
        String defaultCheckin = sdf.format(cal.getTime());
        cal.add(Calendar.DAY_OF_YEAR, 1);
        String defaultCheckout = sdf.format(cal.getTime());
        adapter = new PropertyAdapter(requireContext(), wishlist, defaultCheckin, defaultCheckout);
        rvWishlist.setAdapter(adapter);

        return view;
    }

    @Override
    public void onResume() {
        super.onResume();
        loadWishlist();
    }

    private void loadWishlist() {
        wishlist.clear();
        SharedPreferences pref = requireActivity().getSharedPreferences("AgodaWishlist", Context.MODE_PRIVATE);
        Map<String, ?> allEntries = pref.getAll();
        Gson gson = new Gson();

        for (Map.Entry<String, ?> entry : allEntries.entrySet()) {
            if (entry.getValue() instanceof String) {
                try {
                    Property property = gson.fromJson((String) entry.getValue(), Property.class);
                    if (property != null) {
                        wishlist.add(property);
                    }
                } catch (Exception e) {
                    // Ignore malformed json
                }
            }
        }

        adapter.notifyDataSetChanged();

        if (wishlist.isEmpty()) {
            layoutEmptyWishlist.setVisibility(View.VISIBLE);
            rvWishlist.setVisibility(View.GONE);
        } else {
            layoutEmptyWishlist.setVisibility(View.GONE);
            rvWishlist.setVisibility(View.VISIBLE);
        }
    }
}
