package com.example.android_app.adapters;

import android.content.Context;
import android.content.Intent;
import android.graphics.Paint;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.RatingBar;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;
import com.bumptech.glide.load.resource.drawable.DrawableTransitionOptions;
import com.example.android_app.DetailActivity;
import com.example.android_app.R;
import com.example.android_app.models.Hotel;

import java.util.List;

public class HotelAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {

    private Context context;
    private List<Hotel> hotelList;

    private static final int VIEW_TYPE_ITEM = 0;
    private static final int VIEW_TYPE_LOADING = 1;

    public HotelAdapter(Context context, List<Hotel> hotelList) {
        this.context = context;
        this.hotelList = hotelList;
    }

    @Override
    public int getItemViewType(int position) {
        return (hotelList.get(position) == null || hotelList.get(position).isLoading()) ? VIEW_TYPE_LOADING : VIEW_TYPE_ITEM;
    }

    @NonNull
    @Override
    public RecyclerView.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        if (viewType == VIEW_TYPE_ITEM) {
            View view = LayoutInflater.from(context).inflate(R.layout.item_hotel, parent, false);
            return new HotelViewHolder(view);
        } else {
            View view = LayoutInflater.from(context).inflate(R.layout.item_hotel_placeholder, parent, false);
            return new LoadingViewHolder(view);
        }
    }

    @Override
    public void onBindViewHolder(@NonNull RecyclerView.ViewHolder holder, int position) {
        // 1. Xử lý trường hợp Loading (Skeleton)
        if (holder instanceof LoadingViewHolder) {
            return; // Không làm gì cả, để Shimmer tự chạy
        }

        // 2. Xử lý trường hợp Hiện dữ liệu (Item)
        if (holder instanceof HotelViewHolder) {
            Hotel hotel = hotelList.get(position);
            HotelViewHolder hotelHolder = (HotelViewHolder) holder;

            // --- ĐIỂM SỐ VÀ NHẬN XÉT ---

            if (hotelHolder.tvScoreBox != null) {
                hotelHolder.tvScoreBox.setText(String.valueOf(hotel.getScore()));
            }

            if (hotelHolder.tvReviewCount != null) {
                hotelHolder.tvReviewCount.setText(hotel.getReviewCount() + " nhận xét");
            }

            // --- XỬ LÝ GIÁ VÀ KHUYẾN MÃI (ĐÃ FIX LOGIC THẬT) ---

            // Hiển thị giá bán cuối cùng (luôn hiện)
            if (hotelHolder.tvFinalPrice != null) {
                hotelHolder.tvFinalPrice.setText(String.format(java.util.Locale.US, "%,.0f ₫", hotel.getPrice()));
            }

            // Kiểm tra xem có khuyến mãi thật hay không
            if (hotel.getDiscountPercent() > 0) {
                // Có giảm giá -> Hiện giá gốc gạch chéo
                if (hotelHolder.tvOriginalPrice != null) {
                    hotelHolder.tvOriginalPrice.setVisibility(View.VISIBLE);
                    hotelHolder.tvOriginalPrice.setText(String.format(java.util.Locale.US, "%,.0f ₫", hotel.getOriginalPrice()));
                    hotelHolder.tvOriginalPrice.setPaintFlags(hotelHolder.tvOriginalPrice.getPaintFlags() | Paint.STRIKE_THRU_TEXT_FLAG);
                }

                // Hiện cái badge % đỏ (Giả sử id trong layout của bạn là tvDiscountBadge)
                if (hotelHolder.tvDiscountBadge != null) {
                    hotelHolder.tvDiscountBadge.setVisibility(View.VISIBLE);
                    hotelHolder.tvDiscountBadge.setText("-" + hotel.getDiscountPercent() + "%");
                }
            } else {
                // Không có giảm giá -> Ẩn giá gốc và badge đi cho gọn UI
                if (hotelHolder.tvOriginalPrice != null) {
                    hotelHolder.tvOriginalPrice.setVisibility(View.GONE);
                }
                if (hotelHolder.tvDiscountBadge != null) {
                    hotelHolder.tvDiscountBadge.setVisibility(View.GONE);
                }
            }

            // --- CÁC THÔNG TIN CƠ BẢN KHÁC ---

            if (hotelHolder.tvHotelName != null) hotelHolder.tvHotelName.setText(hotel.getName());
            if (hotelHolder.tvAddress != null) hotelHolder.tvAddress.setText(hotel.getAddress());

            // Làm cho chữ xếp loại linh hoạt theo điểm số
            if (hotelHolder.tvRatingText != null) {
                String ratingText = "Tuyệt vời";
                if (hotel.getScore() < 7.0) ratingText = "Khá tốt";
                else if (hotel.getScore() < 8.5) ratingText = "Rất tốt";

                hotelHolder.tvRatingText.setText(ratingText);
            }

            // RatingBar (Sao)
            if (hotelHolder.ratingBar != null) {
                hotelHolder.ratingBar.setRating((float) hotel.getStarRating());
            }

            // Nhãn Yêu thích
            if (hotelHolder.tvPreferredLabel != null) {
                hotelHolder.tvPreferredLabel.setVisibility(hotel.isPreferred() ? View.VISIBLE : View.GONE);
            }

            // Load ảnh bằng Glide
            if (hotelHolder.imgHotel != null) {
                Glide.with(context)
                        .load(hotel.getImageUrl())
                        .placeholder(R.drawable.bg_search_bar) // Ảnh chờ (nhẹ)
                        .error(R.drawable.ic_launcher_background) // Ảnh lỗi
                        .into(hotelHolder.imgHotel);
            }

            // Sự kiện Click vào khách sạn
            hotelHolder.itemView.setOnClickListener(v -> {
                Intent intent = new Intent(context, DetailActivity.class);
                intent.putExtra("hotel_data", hotel);
                context.startActivity(intent);
            });
        }
    }

    @Override
    public int getItemCount() {
        return hotelList != null ? hotelList.size() : 0;
    }

    // --- VIEW HOLDER ---
    public static class HotelViewHolder extends RecyclerView.ViewHolder {
        ImageView imgHotel;
        TextView tvHotelName, tvAddress;
        RatingBar ratingBar;

        // Các View mới chuẩn Agoda
        TextView tvScoreBox, tvRatingText, tvReviewCount, tvPreferredLabel;

        // View Giá
        LinearLayout layoutAvailable, layoutSoldOut;
        TextView tvDiscountBadge, tvOriginalPrice, tvFinalPrice, tvSoldOutPrice;

        public HotelViewHolder(@NonNull View itemView) {
            super(itemView);
            imgHotel = itemView.findViewById(R.id.imgHotel);
            tvHotelName = itemView.findViewById(R.id.tvHotelName);
            tvAddress = itemView.findViewById(R.id.tvAddress);
            ratingBar = itemView.findViewById(R.id.ratingBar); // ID đã có trong XML mới

            // Ánh xạ View mới
            tvScoreBox = itemView.findViewById(R.id.tvScoreBox);
            tvRatingText = itemView.findViewById(R.id.tvRatingText);
            tvReviewCount = itemView.findViewById(R.id.tvReviewCount);
            tvPreferredLabel = itemView.findViewById(R.id.tvPreferredLabel);

            // Ánh xạ View Giá
            layoutAvailable = itemView.findViewById(R.id.layoutAvailable);
            layoutSoldOut = itemView.findViewById(R.id.layoutSoldOut);
            tvDiscountBadge = itemView.findViewById(R.id.tvDiscountBadge);
            tvOriginalPrice = itemView.findViewById(R.id.tvOriginalPrice);
            tvFinalPrice = itemView.findViewById(R.id.tvFinalPrice);
            tvSoldOutPrice = itemView.findViewById(R.id.tvSoldOutPrice);
        }
    }

    public static class LoadingViewHolder extends RecyclerView.ViewHolder {
        public LoadingViewHolder(@NonNull View itemView) {
            super(itemView);
        }
    }
}