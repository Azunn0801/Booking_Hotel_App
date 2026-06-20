import os
import sys
import time

# Ensure app module can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import rapidapi_get
from app import seed
from app.database import engine
from app import models

CITIES = [
    {"name": "Hà Nội", "id": "1_16694"},
    {"name": "Hồ Chí Minh", "id": "1_13170"},
    {"name": "Vũng Tàu", "id": "1_17190"},
    {"name": "Đà Nẵng", "id": "1_16440"},
    {"name": "Nha Trang", "id": "1_16698"}
]

def reset_db():
    print("Dropping old tables...")
    models.Base.metadata.drop_all(bind=engine)
    
    # Recreate tables
    models.Base.metadata.create_all(bind=engine)
    print("Created fresh database schema.")
    
    # Run user/promo seed
    seed.seed_promotions()
    seed.seed_sample_user()

def seed_rapidapi():
    print("Starting RapidAPI seed...")
    for city in CITIES:
        print(f"\nFetching hotels for {city['name']} (ID: {city['id']})...")
        params = {
            "id": city['id'],
            "checkinDate": "2026-06-20", # Tương lai
            "checkoutDate": "2026-06-21",
            "sort": "Ranking,Desc",
            "language": "vi-vn",
            "room": "1",
            "adult": "2",
            "limit": "20" # Giảm limit xuống 20 để tránh quá tải, đủ test
        }
        try:
            # rapidapi_get will automatically cache the result in the api_cache table
            data = rapidapi_get("/hotels/search-overnight", params)
            if data and data.get("data") and data["data"].get("citySearch"):
                props = data["data"]["citySearch"].get("properties", [])
                print(f"✅ Success! Fetched and cached {len(props)} properties for {city['name']}.")
                
                # Fetch details for the top 3 hotels to ensure we have deep cached data for testing
                top_props = props[:3]
                print(f"   Fetching deep details for top {len(top_props)} hotels in {city['name']}...")
                for p in top_props:
                    pid = str(p.get("propertyId"))
                    if not pid: continue
                    print(f"   -> Caching details for hotel {pid}...")
                    
                    # 1. Details
                    rapidapi_get("/hotels/details", {"propertyId": pid, "language": "vi-vn"})
                    
                    # 1.5 Details Others
                    rapidapi_get("/hotels/details-others", {
                        "propertyId": pid, 
                        "checkinDate": "2026-06-20", 
                        "checkoutDate": "2026-06-21",
                        "language": "vi-vn",
                        "currency": "VND"
                    })
                    
                    # 2. Room prices
                    rapidapi_get("/hotels/room-prices", {
                        "propertyId": pid, 
                        "checkinDate": "2026-06-20", 
                        "checkoutDate": "2026-06-21",
                        "room": "1",
                        "adult": "2",
                        "language": "vi-vn",
                        "currency": "VND"
                    })
                    
                    # 2.5 Room grid
                    rapidapi_get("/hotels/room-grid", {
                        "propertyId": pid, 
                        "checkinDate": "2026-06-20", 
                        "checkoutDate": "2026-06-21",
                        "room": "1",
                        "adult": "2",
                        "language": "vi-vn",
                        "currency": "VND"
                    })
                    
                    # 3. Reviews
                    rapidapi_get("/hotels/reviews", {
                        "propertyId": pid,
                        "reviewSources": "-1",
                        "sort": "7",
                        "page": "1",
                        "limit": "20",
                        "language": "vi-vn"
                    })
                    
                    time.sleep(1) # Sleep to avoid rate limiting
            else:
                print(f"❌ Failed to fetch data for {city['name']}.")
        except Exception as e:
            print(f"❌ Error fetching {city['name']}: {e}")

if __name__ == "__main__":
    reset_db()
    seed_rapidapi()
    print("\n✅ SEED COMPLETE!")
