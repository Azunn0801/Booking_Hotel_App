package com.example.android_app.network;

import com.example.android_app.models.*;
import com.example.android_app.models.UserLoginRequest;

import java.util.List;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.GET;
import retrofit2.http.POST;
import retrofit2.http.PUT;
import retrofit2.http.Path;
import retrofit2.http.Query;

public interface ApiService {

    // =====================================================================
    // AUTOCOMPLETE - Tìm kiếm thành phố
    // =====================================================================
    @GET("api/autocomplete")
    Call<List<AutoCompleteResult>> autocomplete(
            @Query("query") String query,
            @Query("language") String language
    );

    // =====================================================================
    // PROPERTY SEARCH - Tìm kiếm khách sạn/căn hộ/villa
    // =====================================================================
    @GET("api/properties/search")
    Call<SearchResponse> searchProperties(
            @Query("city_id") String cityId,
            @Query("checkin") String checkin,
            @Query("checkout") String checkout,
            @Query("property_type") String propertyType,
            @Query("star_rating") String starRating,
            @Query("min_price") Double minPrice,
            @Query("max_price") Double maxPrice,
            @Query("sort") String sort,
            @Query("limit") Integer limit,
            @Query("include_filters") Boolean includeFilters
    );

    // =====================================================================
    // PROPERTY DETAILS - Chi tiết property
    // =====================================================================
    @GET("api/properties/{property_id}/details")
    Call<PropertyDetail> getPropertyDetails(
            @Path("property_id") String propertyId
    );

    // =====================================================================
    // ROOM PRICES - Giá phòng
    // =====================================================================
    @GET("api/properties/{property_id}/rooms")
    Call<List<Room>> getPropertyRooms(
            @Path("property_id") String propertyId,
            @Query("checkin") String checkin,
            @Query("checkout") String checkout
    );

    // =====================================================================
    // REVIEWS - Đánh giá
    // =====================================================================
    @GET("api/properties/{property_id}/reviews")
    Call<Object> getPropertyReviews(
            @Path("property_id") String propertyId
    );

    // =====================================================================
    // AUTH - Đăng nhập/Đăng ký
    // =====================================================================
    @POST("auth/login")
    Call<LoginResponse> loginUser(
            @Body UserLoginRequest request
    );

    @POST("auth/register")
    Call<Void> registerUser(
            @Body UserCreateRequest request
    );

    @PUT("auth/profile/{user_id}")
    Call<LoginResponse> updateProfile(
            @Path("user_id") int userId,
            @Body ProfileUpdateRequest request
    );

    // =====================================================================
    // BOOKINGS - Đặt chỗ
    // =====================================================================
    @POST("bookings")
    Call<BookingResponse> createBooking(
            @Body BookingRequest request
    );

    @GET("bookings/{user_id}")
    Call<List<BookingResponse>> getUserBookings(
            @Path("user_id") int userId
    );

    // =====================================================================
    // PROMOTIONS - Khuyến mãi
    // =====================================================================
    @GET("api/promotions")
    Call<List<Promotion>> getPromotions();

    @POST("api/promotions/apply")
    Call<PromoApplyResponse> applyPromotion(
            @Body PromoApplyRequest request
    );

    // =====================================================================
    // UTILITIES
    // =====================================================================
    @GET("languages")
    Call<List<Language>> getLanguages();

    @GET("currencies")
    Call<List<Currency>> getCurrencies();
}
