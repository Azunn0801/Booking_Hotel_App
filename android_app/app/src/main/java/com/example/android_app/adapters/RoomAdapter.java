package com.example.android_app.adapters;

import android.content.Context;
import android.content.Intent;
import android.graphics.Paint;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.HorizontalScrollView;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;
import com.example.android_app.CheckoutActivity;
import com.example.android_app.R;
import com.example.android_app.models.Property;
import com.example.android_app.models.Room;

import java.util.List;
import java.util.Locale;

public class RoomAdapter extends RecyclerView.Adapter<RoomAdapter.RoomViewHolder> {

    private Context context;
    private List<Room> roomList;
    private Property property;
    private String checkInDate;
    private String checkOutDate;

    public RoomAdapter(Context context, List<Room> roomList, Property property, String checkInDate, String checkOutDate) {
        this.context = context;
        this.roomList = roomList;
        this.property = property;
        this.checkInDate = checkInDate;
        this.checkOutDate = checkOutDate;
    }

    @NonNull
    @Override
    public RoomViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.item_room, parent, false);
        return new RoomViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull RoomViewHolder holder, int position) {
        Room room = roomList.get(position);
        holder.tvName.setText(room.getRoomName());

        // Price display
        holder.tvPrice.setText(String.format(Locale.US, "%,.0f VND", (double) room.getPrice()));

        // Original price
        if (room.getOriginalPrice() > room.getPrice()) {
            holder.tvOriginalPrice.setVisibility(View.VISIBLE);
            holder.tvOriginalPrice.setText(String.format(Locale.US, "%,.0f VND", room.getOriginalPrice()));
            holder.tvOriginalPrice.setPaintFlags(holder.tvOriginalPrice.getPaintFlags() | Paint.STRIKE_THRU_TEXT_FLAG);
        } else {
            holder.tvOriginalPrice.setVisibility(View.GONE);
        }

        // Amenities
        holder.tvAmenities.setText(room.getAmenities() != null ? room.getAmenities() : "Đầy đủ tiện nghi");

        // Occupancy
        holder.tvOccupancy.setText(room.getRoomOccupancyDescription() != null ? room.getRoomOccupancyDescription() : "Tối đa 2 người lớn");

        // Badges
        holder.tvBreakfastBadge.setVisibility(room.isBreakfastIncluded() ? View.VISIBLE : View.GONE);
        holder.tvCancellationBadge.setVisibility(room.isFreeCancellation() ? View.VISIBLE : View.GONE);
        
        if (room.getRemainRoom() > 0 && room.getRemainRoom() <= 3) {
            holder.tvRemainBadge.setVisibility(View.VISIBLE);
            holder.tvRemainBadge.setText("🔥 Chỉ còn " + room.getRemainRoom() + " phòng giá này!");
        } else {
            holder.tvRemainBadge.setVisibility(View.GONE);
        }

        // Horizontal Gallery for Room Images
        List<String> images = room.getImages();
        if (images != null && !images.isEmpty()) {
            holder.hsvRoomImages.setVisibility(View.VISIBLE);
            holder.layoutRoomImages.removeAllViews();
            for (String url : images) {
                ImageView iv = new ImageView(context);
                int width = (int) (280 * context.getResources().getDisplayMetrics().density);
                LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(width, ViewGroup.LayoutParams.MATCH_PARENT);
                lp.setMargins(0, 0, 12, 0);
                iv.setLayoutParams(lp);
                iv.setScaleType(ImageView.ScaleType.CENTER_CROP);
                
                Glide.with(context)
                        .load(url)
                        .placeholder(android.R.color.darker_gray)
                        .into(iv);
                
                holder.layoutRoomImages.addView(iv);
            }
        } else {
            holder.hsvRoomImages.setVisibility(View.GONE);
        }

        holder.btnBook.setOnClickListener(v -> {
            Intent intent = new Intent(context, CheckoutActivity.class);
            intent.putExtra("property_data", property);
            intent.putExtra("room_data", room);
            intent.putExtra("checkin_date", checkInDate);
            intent.putExtra("checkout_date", checkOutDate);
            context.startActivity(intent);
        });
    }

    @Override
    public int getItemCount() {
        return roomList != null ? roomList.size() : 0;
    }

    public static class RoomViewHolder extends RecyclerView.ViewHolder {
        TextView tvName, tvPrice, tvAmenities, tvOriginalPrice;
        TextView tvOccupancy, tvBreakfastBadge, tvCancellationBadge, tvRemainBadge;
        Button btnBook;
        HorizontalScrollView hsvRoomImages;
        LinearLayout layoutRoomImages;

        public RoomViewHolder(@NonNull View itemView) {
            super(itemView);
            tvName = itemView.findViewById(R.id.tvRoomName);
            tvPrice = itemView.findViewById(R.id.tvRoomPrice);
            tvAmenities = itemView.findViewById(R.id.tvRoomAmenities);
            tvOriginalPrice = itemView.findViewById(R.id.tvOriginalPrice);
            tvOccupancy = itemView.findViewById(R.id.tvOccupancy);
            tvBreakfastBadge = itemView.findViewById(R.id.tvBreakfastBadge);
            tvCancellationBadge = itemView.findViewById(R.id.tvCancellationBadge);
            tvRemainBadge = itemView.findViewById(R.id.tvRemainBadge);
            btnBook = itemView.findViewById(R.id.btnBook);
            hsvRoomImages = itemView.findViewById(R.id.hsvRoomImages);
            layoutRoomImages = itemView.findViewById(R.id.layoutRoomImages);
        }
    }
}