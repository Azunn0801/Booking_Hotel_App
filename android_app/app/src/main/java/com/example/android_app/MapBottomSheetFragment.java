package com.example.android_app;

import android.app.Dialog;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.example.android_app.models.Hotel;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.LatLngBounds;
import com.google.android.gms.maps.model.MarkerOptions;
import com.google.android.material.bottomsheet.BottomSheetBehavior;
import com.google.android.material.bottomsheet.BottomSheetDialog;
import com.google.android.material.bottomsheet.BottomSheetDialogFragment;

import java.io.Serializable;
import java.util.List;

public class MapBottomSheetFragment extends BottomSheetDialogFragment implements OnMapReadyCallback {

    private List<Hotel> hotelList;

    // Cách khởi tạo chuẩn để truyền dữ liệu an toàn
    public static MapBottomSheetFragment newInstance(List<Hotel> hotels) {
        MapBottomSheetFragment fragment = new MapBottomSheetFragment();
        Bundle args = new Bundle();
        args.putSerializable("hotels", (Serializable) hotels);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            hotelList = (List<Hotel>) getArguments().getSerializable("hotels");
        }
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.layout_map_bottom_sheet, container, false);

        // Nút đóng bản đồ
        view.findViewById(R.id.btnCloseMap).setOnClickListener(v -> dismiss());

        // Khởi tạo Google Maps
        SupportMapFragment mapFragment = (SupportMapFragment) getChildFragmentManager().findFragmentById(R.id.map);
        if (mapFragment != null) {
            mapFragment.getMapAsync(this);
        }

        return view;
    }

    @Override
    public void onMapReady(@NonNull GoogleMap googleMap) {
        if (hotelList == null || hotelList.isEmpty()) return;

        LatLngBounds.Builder builder = new LatLngBounds.Builder();
        boolean hasPoints = false;

        for (Hotel hotel : hotelList) {
            // Kiểm tra nếu hotel có tọa độ (Tránh văng app nếu lat/lng = 0)
            if (!hotel.isLoading() && hotel.getLatitude() != 0) {
                LatLng pos = new LatLng(hotel.getLatitude(), hotel.getLongitude());
                googleMap.addMarker(new MarkerOptions()
                        .position(pos)
                        .title(hotel.getName())
                        .snippet(String.format("₫ %,.0f", hotel.getPrice())));

                builder.include(pos);
                hasPoints = true;
            }
        }

        // Tự động căn chỉnh Map để nhìn thấy toàn bộ Marker
        if (hasPoints) {
            googleMap.setOnMapLoadedCallback(() -> {
                googleMap.animateCamera(CameraUpdateFactory.newLatLngBounds(builder.build(), 150));
            });
        }
    }

    // Cấu hình Full màn hình giống Agoda
    @NonNull
    @Override
    public Dialog onCreateDialog(@Nullable Bundle savedInstanceState) {
        BottomSheetDialog dialog = (BottomSheetDialog) super.onCreateDialog(savedInstanceState);
        dialog.setOnShowListener(d -> {
            FrameLayout bottomSheet = ((BottomSheetDialog) d).findViewById(com.google.android.material.R.id.design_bottom_sheet);
            if (bottomSheet != null) {
                bottomSheet.getLayoutParams().height = ViewGroup.LayoutParams.MATCH_PARENT;
                BottomSheetBehavior.from(bottomSheet).setState(BottomSheetBehavior.STATE_EXPANDED);
            }
        });
        return dialog;
    }
}