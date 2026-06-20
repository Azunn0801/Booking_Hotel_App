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
import com.example.android_app.models.Property;
import com.google.gson.Gson;

import java.util.List;

public class PropertyAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {

    private Context context;
    private List<Property> propertyList;
    private String checkInDate;
    private String checkOutDate;

    private static final int VIEW_TYPE_ITEM = 0;
    private static final int VIEW_TYPE_LOADING = 1;

    public PropertyAdapter(Context context, List<Property> propertyList, String checkInDate, String checkOutDate) {
        this.context = context;
        this.propertyList = propertyList;
        this.checkInDate = checkInDate;
        this.checkOutDate = checkOutDate;
    }

    @Override
    public int getItemViewType(int position) {
        Property p = propertyList.get(position);
        return (p == null || p.isLoading()) ? VIEW_TYPE_LOADING : VIEW_TYPE_ITEM;
    }

    @NonNull
    @Override
    public RecyclerView.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        if (viewType == VIEW_TYPE_ITEM) {
            View view = LayoutInflater.from(context).inflate(R.layout.item_hotel, parent, false);
            return new PropertyViewHolder(view);
        } else {
            View view = LayoutInflater.from(context).inflate(R.layout.item_hotel_placeholder, parent, false);
            return new LoadingViewHolder(view);
        }
    }

    @Override
    public void onBindViewHolder(@NonNull RecyclerView.ViewHolder holder, int position) {
        if (holder instanceof LoadingViewHolder) return;

        if (holder instanceof PropertyViewHolder) {
            Property property = propertyList.get(position);
            PropertyViewHolder h = (PropertyViewHolder) holder;

            // Score
            if (h.tvScoreBox != null) {
                h.tvScoreBox.setText(String.valueOf(property.getScore()));
            }

            // Review count
            if (h.tvReviewCount != null) {
                h.tvReviewCount.setText(property.getReviewCount() + " nhan xet");
            }

            // Final price
            if (h.tvFinalPrice != null) {
                h.tvFinalPrice.setText(String.format(java.util.Locale.US, "%,.0f VND", property.getPrice()));
            }

            // Discount
            if (property.getDiscountPercent() > 0) {
                if (h.tvOriginalPrice != null) {
                    h.tvOriginalPrice.setVisibility(View.VISIBLE);
                    h.tvOriginalPrice.setText(String.format(java.util.Locale.US, "%,.0f VND", property.getOriginalPrice()));
                    h.tvOriginalPrice.setPaintFlags(h.tvOriginalPrice.getPaintFlags() | Paint.STRIKE_THRU_TEXT_FLAG);
                }
                if (h.tvDiscountBadge != null) {
                    h.tvDiscountBadge.setVisibility(View.VISIBLE);
                    h.tvDiscountBadge.setText("-" + property.getDiscountPercent() + "%");
                }
            } else {
                if (h.tvOriginalPrice != null) h.tvOriginalPrice.setVisibility(View.GONE);
                if (h.tvDiscountBadge != null) h.tvDiscountBadge.setVisibility(View.GONE);
            }

            // Property type badge
            if (h.tvPropertyTypeBadge != null) {
                String propType = property.getPropertyType();
                if (propType != null && !propType.isEmpty()) {
                    h.tvPropertyTypeBadge.setVisibility(View.VISIBLE);
                    switch (propType) {
                        case "hotel":
                            h.tvPropertyTypeBadge.setText("Khach san");
                            h.tvPropertyTypeBadge.setBackgroundColor(ContextCompat.getColor(context, android.R.color.holo_blue_light));
                            break;
                        case "apartment":
                            h.tvPropertyTypeBadge.setText("Can ho");
                            h.tvPropertyTypeBadge.setBackgroundColor(ContextCompat.getColor(context, android.R.color.holo_green_light));
                            break;
                        case "villa":
                            h.tvPropertyTypeBadge.setText("Villa");
                            h.tvPropertyTypeBadge.setBackgroundColor(ContextCompat.getColor(context, android.R.color.holo_orange_light));
                            break;
                        default:
                            h.tvPropertyTypeBadge.setText(propType);
                            break;
                    }
                } else {
                    h.tvPropertyTypeBadge.setVisibility(View.GONE);
                }
            }

            // Name & address
            if (h.tvHotelName != null) h.tvHotelName.setText(property.getName());
            if (h.tvAddress != null) {
                String address = property.getAddress() != null ? property.getAddress() : "";
                if (property.getDistanceDescription() != null && !property.getDistanceDescription().isEmpty()) {
                    address += " • " + property.getDistanceDescription();
                }
                h.tvAddress.setText(address);
            }

            // Rating text
            if (h.tvRatingText != null) {
                String ratingText = property.getReviewQuote();
                if (ratingText == null || ratingText.isEmpty()) {
                    ratingText = "Tuyệt vời";
                    if (property.getScore() < 7.0) ratingText = "Khá tốt";
                    else if (property.getScore() < 8.5) ratingText = "Rất tốt";
                }
                h.tvRatingText.setText(ratingText);
            }

            // Star rating
            if (h.ratingBar != null) {
                h.ratingBar.setRating(property.getStarRating());
            }

            // Preferred label
            if (h.tvPreferredLabel != null) {
                h.tvPreferredLabel.setVisibility(property.isPreferred() ? View.VISIBLE : View.GONE);
            }

            // Image
            if (h.imgHotel != null) {
                Glide.with(context)
                        .load(property.getImageUrl())
                        .placeholder(R.drawable.bg_search_bar)
                        .error(R.drawable.ic_launcher_background)
                        .into(h.imgHotel);
            }

            // Wishlist
            SharedPreferences pref = context.getSharedPreferences("AgodaWishlist", Context.MODE_PRIVATE);
            Gson gson = new Gson();
            final boolean[] isSaved = {pref.contains(property.getId())};

            if (h.btnWishlistHeart != null) {
                h.btnWishlistHeart.setColorFilter(ContextCompat.getColor(context,
                        isSaved[0] ? android.R.color.holo_red_dark : android.R.color.darker_gray));

                h.btnWishlistHeart.setOnClickListener(v -> {
                    SharedPreferences.Editor editor = pref.edit();
                    if (isSaved[0]) {
                        editor.remove(property.getId()).apply();
                        h.btnWishlistHeart.setColorFilter(ContextCompat.getColor(context, android.R.color.darker_gray));
                        Toast.makeText(context, "Da xoa khoi yeu thich", Toast.LENGTH_SHORT).show();
                        isSaved[0] = false;
                    } else {
                        editor.putString(property.getId(), gson.toJson(property)).apply();
                        h.btnWishlistHeart.setColorFilter(ContextCompat.getColor(context, android.R.color.holo_red_dark));
                        Toast.makeText(context, "Da them vao yeu thich", Toast.LENGTH_SHORT).show();
                        isSaved[0] = true;
                    }
                });
            }

            // Click to detail
            h.itemView.setOnClickListener(v -> {
                Intent intent = new Intent(context, DetailActivity.class);
                intent.putExtra("property_data", property);
                if (checkInDate != null) intent.putExtra("checkin_date", checkInDate);
                if (checkOutDate != null) intent.putExtra("checkout_date", checkOutDate);
                context.startActivity(intent);
            });
        }
    }

    @Override
    public int getItemCount() {
        return propertyList != null ? propertyList.size() : 0;
    }

    public static class PropertyViewHolder extends RecyclerView.ViewHolder {
        ImageView imgHotel;
        TextView tvHotelName, tvAddress, tvPropertyTypeBadge;
        RatingBar ratingBar;
        TextView tvScoreBox, tvRatingText, tvReviewCount, tvPreferredLabel;
        ImageButton btnWishlistHeart;
        LinearLayout layoutAvailable, layoutSoldOut;
        TextView tvDiscountBadge, tvOriginalPrice, tvFinalPrice, tvSoldOutPrice;

        public PropertyViewHolder(@NonNull View itemView) {
            super(itemView);
            imgHotel = itemView.findViewById(R.id.imgHotel);
            tvHotelName = itemView.findViewById(R.id.tvHotelName);
            tvAddress = itemView.findViewById(R.id.tvAddress);
            // [FIX A15] tvPropertyTypeBadge phải được bind — trước đây bị comment là null
            tvPropertyTypeBadge = itemView.findViewById(R.id.tvPropertyTypeBadge);
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
