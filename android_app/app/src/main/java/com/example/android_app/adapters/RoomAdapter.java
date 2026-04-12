package com.example.android_app.adapters;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.example.android_app.R;
import com.example.android_app.models.Room;
import java.util.List;

public class RoomAdapter extends RecyclerView.Adapter<RoomAdapter.RoomViewHolder> {

    private Context context;
    private List<Room> roomList;

    public RoomAdapter(Context context, List<Room> roomList) {
        this.context = context;
        this.roomList = roomList;
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
        holder.tvPrice.setText(room.getPrice() + " $");
        holder.tvAmenities.setText("Tiện nghi: " + room.getAmenities());

        holder.btnBook.setOnClickListener(v -> {
            Toast.makeText(context, "Đang chuẩn bị đơn đặt phòng cho: " + room.getRoomName(), Toast.LENGTH_SHORT).show();
            // Bước sau sẽ gọi API POST /bookings ở đây
        });
    }

    @Override
    public int getItemCount() {
        return roomList.size();
    }

    public static class RoomViewHolder extends RecyclerView.ViewHolder {
        TextView tvName, tvPrice, tvAmenities;
        Button btnBook;

        public RoomViewHolder(@NonNull View itemView) {
            super(itemView);
            tvName = itemView.findViewById(R.id.tvRoomName);
            tvPrice = itemView.findViewById(R.id.tvRoomPrice);
            tvAmenities = itemView.findViewById(R.id.tvRoomAmenities);
            btnBook = itemView.findViewById(R.id.btnBook);
        }
    }
}