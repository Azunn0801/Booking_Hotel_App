package com.example.android_app.network;

import com.example.android_app.models.Room;
import com.example.android_app.models.Hotel;
import java.util.List;
import retrofit2.Call;
import retrofit2.http.GET;
import retrofit2.http.Path;
import retrofit2.http.Query;

public interface ApiService {
    @GET("hotels/search-overnight")
    Call<List<Hotel>> searchHotels(
            @Query("id") String cityId,
            @Query("starRating") String starRating,
            @Query("prices") String prices,
            @Query("sort") String sort
    );

    // SỬA: Đổi int thành String cho hotel_id
    @GET("hotels/details")
    Call<Hotel> getHotelDetails(@Query("hotel_id") String hotelId);

    // SỬA: Đổi int thành String cho hotel_id
    @GET("hotels/{hotel_id}/rooms")
    Call<List<Room>> getHotelRooms(@Path("hotel_id") String hotelId);

    @GET("/hotels/room-prices")
    Call<List<Room>> getRoomPrices(@Query("hotel_id") int hotelId);
}