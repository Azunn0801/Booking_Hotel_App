package com.example.android_app.adapters;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Paint;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.RatingBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;
import com.example.android_app.DetailActivity;
import com.example.android_app.R;
import com.example.android_app.models.Hotel;
import com.google.gson.Gson;

import java.util.List;

public class HotelAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {

    private Context context;
    private List<Hotel> hotelList;
    private String checkInDate;
    private String checkOutDate;

    private static final int VIEW_TYPE_ITEM = 0;
    private static final int VIEW_TYPE_LOADING = 1;

    public HotelAdapter(Context context, List<Hotel> hotelList) {
        this.context = context;
        this.hotelList = hotelList;
        this.checkInDate = null;
        this.checkOutDate = null;
    }

    public HotelAdapter(Context context, List<Hotel> hotelList, String checkInDate, String checkOutDate) {
        this.context = context;
        this.hotelList = hotelList;
        this.checkInDate = checkInDate;
        this.checkOutDate = checkOutDate;
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
        // 1. Xu ly truong hop Loading (Skeleton)
        if (holder instanceof LoadingViewHolder) {
            return; // Khong lam gi ca, de Shimmer tu chay
        }

        // 2. Xu ly truong hop Hien du lieu (Item)
        if (holder instanceof HotelViewHolder) {
            Hotel hotel = hotelList.get(position);
            HotelViewHolder hotelHolder = (HotelViewHolder) holder;

            // --- DIEM SO VA NHAN XET ---

            if (hotelHolder.tvScoreBox != null) {
                hotelHolder.tvScoreBox.setText(String.valueOf(hotel.getScore()));
            }

            if (hotelHolder.tvReviewCount != null) {
                hotelHolder.tvReviewCount.setText(hotel.getReviewCount() + " nhan xet");
            }

            // --- XU LY GIA VA KHUYEN MAI ---

            // Hien thi gia ban cuoi cung (luon hien)
            if (hotelHolder.tvFinalPrice != null) {
                hotelHolder.tvFinalPrice.setText(String.format(java.util.Locale.US, "%,.0f VND", hotel.getPrice()));
            }

            // Kiem tra xem co khuyen mai that hay khong
            if (hotel.getDiscountPercent() > 0) {
                // Co giam gia -> Hien gia goc gach cheo
                if (hotelHolder.tvOriginalPrice != null) {
                    hotelHolder.tvOriginalPrice.setVisibility(View.VISIBLE);
                    hotelHolder.tvOriginalPrice.setText(String.format(java.util.Locale.US, "%,.0f VND", hotel.getOriginalPrice()));
                    hotelHolder.tvOriginalPrice.setPaintFlags(hotelHolder.tvOriginalPrice.getPaintFlags() | Paint.STRIKE_THRU_TEXT_FLAG);
                }

                // Hien badge % do
                if (hotelHolder.tvDiscountBadge != null) {
                    hotelHolder.tvDiscountBadge.setVisibility(View.VISIBLE);
                    hotelHolder.tvDiscountBadge.setText("-" + hotel.getDiscountPercent() + "%");
                }
            } else {
                // Khong co giam gia -> An gia goc va badge
                if (hotelHolder.tvOriginalPrice != null) {
                    hotelHolder.tvOriginalPrice.setVisibility(View.GONE);
                }
                if (hotelHolder.tvDiscountBadge != null) {
                    hotelHolder.tvDiscountBadge.setVisibility(View.GONE);
                }
            }

            // --- CAC THONG TIN CO BAN KHAC ---

            if (hotelHolder.tvHotelName != null) hotelHolder.tvHotelName.setText(hotel.getName());
            if (hotelHolder.tvAddress != null) hotelHolder.tvAddress.setText(hotel.getAddress());

            // Lam cho chu xep loai linh hoat theo diem so
            if (hotelHolder.tvRatingText != null) {
                String ratingText = "Tuyet voi";
                if (hotel.getScore() < 7.0) ratingText = "Kha tot";
                else if (hotel.getScore() < 8.5) ratingText = "Rat tot";

                hotelHolder.tvRatingText.setText(ratingText);
            }

            // RatingBar (Sao)
            if (hotelHolder.ratingBar != null) {
                hotelHolder.ratingBar.setRating((float) hotel.getStarRating());
            }

            // Nhan Yeu thich
            if (hotelHolder.tvPreferredLabel != null) {
                hotelHolder.tvPreferredLabel.setVisibility(hotel.isPreferred() ? View.VISIBLE : View.GONE);
            }

            // Load anh bang Glide
            if (hotelHolder.imgHotel != null) {
                Glide.with(context)
                        .load(hotel.getImageUrl())
                        .placeholder(R.drawable.bg_search_bar)
                        .error(R.drawable.ic_launcher_background)
                        .into(hotelHolder.imgHotel);
            }

            // Wishlist Toggle Logic
            SharedPreferences pref = context.getSharedPreferences("AgodaWishlist", Context.MODE_PRIVATE);
            Gson gson = new Gson();
            final boolean[] isSaved = {pref.contains(hotel.getId())};

            if (hotelHolder.btnWishlistHeart != null) {
                if (isSaved[0]) {
                    hotelHolder.btnWishlistHeart.setColorFilter(ContextCompat.getColor(context, android.R.color.holo_red_dark));
                } else {
                    hotelHolder.btnWishlistHeart.setColorFilter(ContextCompat.getColor(context, android.R.color.darker_gray));
                }

                hotelHolder.btnWishlistHeart.setOnClickListener(v -> {
                    SharedPreferences.Editor editor = pref.edit();
                    if (isSaved[0]) {
                        editor.remove(hotel.getId()).apply();
                        hotelHolder.btnWishlistHeart.setColorFilter(ContextCompat.getColor(context, android.R.color.darker_gray));
                        Toast.makeText(context, "Da xoa khoi danh sach yeu thich", Toast.LENGTH_SHORT).show();
                        isSaved[0] = false;
                    } else {
                        String hotelJson = gson.toJson(hotel);
                        editor.putString(hotel.getId(), hotelJson).apply();
                        hotelHolder.btnWishlistHeart.setColorFilter(ContextCompat.getColor(context, android.R.color.holo_red_dark));
                        Toast.makeText(context, "Da them vao danh sach yeu thich", Toast.LENGTH_SHORT).show();
                        isSaved[0] = true;
                    }
                });
            }

            // Su kien Click vao khach san
            hotelHolder.itemView.setOnClickListener(v -> {
                Intent intent = new Intent(context, DetailActivity.class);
                intent.putExtra("hotel_data", hotel);
                if (checkInDate != null) intent.putExtra("checkin_date", checkInDate);
                if (checkOutDate != null) intent.putExtra("checkout_date", checkOutDate);
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

        TextView tvScoreBox, tvRatingText, tvReviewCount, tvPreferredLabel;
        ImageButton btnWishlistHeart;

        LinearLayout layoutAvailable, layoutSoldOut;
        TextView tvDiscountBadge, tvOriginalPrice, tvFinalPrice, tvSoldOutPrice;

        public HotelViewHolder(@NonNull View itemView) {
            super(itemView);
            imgHotel = itemView.findViewById(R.id.imgHotel);
            tvHotelName = itemView.findViewById(R.id.tvHotelName);
            tvAddress = itemView.findViewById(R.id.tvAddress);
            ratingBar = itemView.findViewById(R.id.ratingBar);

            tvScoreBox = itemView.findViewById(R.id.tvScoreBox);
            tvRatingText = itemView.findViewById(R.id.tvRatingText);
            tvReviewCount = itemView.findViewById(R.id.tvReviewCount);
            tvPreferredLabel = itemView.findViewById(R.id.tvPreferredLabel);
            btnWishlistHeart = itemView.findViewById(R.id.btnWishlistHeart);

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
