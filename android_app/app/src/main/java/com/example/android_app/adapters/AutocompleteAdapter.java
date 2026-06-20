package com.example.android_app.adapters;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.bumptech.glide.Glide;
import com.example.android_app.R;
import com.example.android_app.models.AutoCompleteResult;

import java.util.List;

public class AutocompleteAdapter extends ArrayAdapter<AutoCompleteResult> {

    public AutocompleteAdapter(@NonNull Context context, @NonNull List<AutoCompleteResult> objects) {
        super(context, 0, objects);
    }

    @NonNull
    @Override
    public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
        if (convertView == null) {
            convertView = LayoutInflater.from(getContext()).inflate(R.layout.item_autocomplete, parent, false);
        }

        AutoCompleteResult item = getItem(position);
        if (item != null) {
            TextView tvCityName = convertView.findViewById(R.id.tvCityName);
            TextView tvCountryName = convertView.findViewById(R.id.tvCountryName);
            TextView tvActiveHotels = convertView.findViewById(R.id.tvActiveHotels);
            ImageView imgCity = convertView.findViewById(R.id.imgCity);

            tvCityName.setText(item.getName() != null ? item.getName() : item.getCityName());
            
            String country = item.getCountryName() != null ? item.getCountryName() : "";
            if (item.getStateName() != null && !item.getStateName().isEmpty()) {
                country = item.getStateName() + ", " + country;
            }
            tvCountryName.setText(country);
            
            tvActiveHotels.setText(item.getActiveHotels() > 0 ? item.getActiveHotels() + " khách sạn" : "");

            if (item.getImageUrl() != null && !item.getImageUrl().isEmpty()) {
                Glide.with(getContext())
                        .load(item.getImageUrl())
                        .placeholder(android.R.drawable.ic_menu_mapmode)
                        .into(imgCity);
            } else {
                imgCity.setImageResource(android.R.drawable.ic_menu_mapmode);
            }
        }

        return convertView;
    }
}
