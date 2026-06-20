package com.example.android_app;

import android.app.Dialog;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.example.android_app.models.Property;
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

    private List<Property> propertyList;

    // Cách khởi tạo chuẩn để truyền dữ liệu an toàn
    public static MapBottomSheetFragment newInstance(List<Property> properties) {
        MapBottomSheetFragment fragment = new MapBottomSheetFragment();
        Bundle args = new Bundle();
        args.putSerializable("properties", (Serializable) properties);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            propertyList = (List<Property>) getArguments().getSerializable("properties");
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
        if (propertyList == null || propertyList.isEmpty()) return;

        LatLngBounds.Builder builder = new LatLngBounds.Builder();
        boolean hasPoints = false;

        for (Property property : propertyList) {
            // Kiểm tra nếu property có tọa độ (Tránh văng app nếu lat/lng = 0)
            if (!property.isLoading() && property.getLatitude() != 0) {
                LatLng pos = new LatLng(property.getLatitude(), property.getLongitude());
                googleMap.addMarker(new MarkerOptions()
                        .position(pos)
                        .title(property.getName())
                        .snippet(String.format("₫ %,.0f", property.getPrice())));

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