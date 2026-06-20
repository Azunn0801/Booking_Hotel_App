package com.example.android_app.adapters;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;
import com.example.android_app.R;
import com.example.android_app.models.BookingResponse;

import java.util.List;

public class BookingAdapter extends RecyclerView.Adapter<BookingAdapter.BookingViewHolder> {

    private Context context;
    private List<BookingResponse> bookingList;

    public BookingAdapter(Context context, List<BookingResponse> bookingList) {
        this.context = context;
        this.bookingList = bookingList;
    }

    @NonNull
    @Override
    public BookingViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.item_booking, parent, false);
        return new BookingViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull BookingViewHolder holder, int position) {
        BookingResponse booking = bookingList.get(position);

        // Tên khách sạn
        holder.tvHotelName.setText(booking.getPropertyName());

        // [FIX A14] Trước đây bị đảo: address hiển thị dates, dates hiển thị price
        // Đúng: address = loại chỗ ở, tvDates = ngày đặt, tvPrice = tổng tiền
        if (holder.tvAddress != null) {
            String addrText = booking.getPropertyType() != null
                    ? labelType(booking.getPropertyType())
                    : "Chỗ ở";
            holder.tvAddress.setText(addrText);
        }

        if (holder.tvDates != null) {
            holder.tvDates.setText(booking.getCheckinDate() + " → " + booking.getCheckoutDate());
        }

        // Property type badge
        if (holder.tvServiceType != null) {
            String propType = booking.getPropertyType();
            if (propType != null) {
                holder.tvServiceType.setVisibility(android.view.View.VISIBLE);
                holder.tvServiceType.setText(labelType(propType));
            } else {
                holder.tvServiceType.setVisibility(android.view.View.GONE);
            }
        }

        // Price
        if (holder.tvPrice != null) {
            holder.tvPrice.setText(String.format(java.util.Locale.US, "%,.0f ₫", booking.getTotalPrice()));
        }

        // Load image
        Glide.with(context)
                .load(booking.getPropertyImage())
                .placeholder(R.drawable.bg_search_bar)
                .error(R.drawable.ic_launcher_background)
                .into(holder.imgHotel);
    }

    private String labelType(String type) {
        if (type == null) return "Chỗ ở";
        switch (type.toLowerCase()) {
            case "hotel": return "Khách sạn";
            case "apartment": return "Căn hộ";
            case "villa": return "Villa";
            case "resort": return "Resort";
            default: return type;
        }
    }

    @Override
    public int getItemCount() {
        return bookingList != null ? bookingList.size() : 0;
    }

    public static class BookingViewHolder extends RecyclerView.ViewHolder {
        ImageView imgHotel;
        TextView tvHotelName, tvAddress, tvDates, tvServiceType, tvPrice;

        public BookingViewHolder(@NonNull View itemView) {
            super(itemView);
            imgHotel = itemView.findViewById(R.id.imgBookingHotel);
            tvHotelName = itemView.findViewById(R.id.tvBookingHotelName);
            tvAddress = itemView.findViewById(R.id.tvBookingAddress);
            tvDates = itemView.findViewById(R.id.tvBookingDates);
            tvServiceType = itemView.findViewById(R.id.tvBookingServiceType);
            tvPrice = itemView.findViewById(R.id.tvBookingPrice);
        }
    }
}
