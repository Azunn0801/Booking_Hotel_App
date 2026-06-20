import json
from app import database, models

db = database.SessionLocal()
try:
    # Lấy cache của room-grid
    grid_caches = db.query(models.ApiCache).filter(models.ApiCache.endpoint == "/hotels/room-grid").all()
    print(f"Found {len(grid_caches)} cached room-grid requests.")
    for idx, cached in enumerate(grid_caches):
        data = json.loads(cached.response_data)
        groups = data.get("roomGroups", [])
        if groups:
            print(f"\n--- Cache room-grid #{idx} ---")
            g = groups[0]
            print("Group keys:", list(g.keys()))
            print("masterRoomTypeName:", g.get("masterRoomTypeName"))
            rooms = g.get("rooms", [])
            if rooms:
                r = rooms[0]
                print("Room keys:", list(r.keys()))
                # In thử một vài trường quan trọng
                print("uid:", r.get("uid"))
                print("images:", r.get("images"))
                print("benefits:", r.get("benefits"))
                print("pricingDisplaySummary keys:", list(r.get("pricingDisplaySummary", {}).keys()))
                
    # Lấy cache của room-prices
    prices_caches = db.query(models.ApiCache).filter(models.ApiCache.endpoint == "/hotels/room-prices").all()
    print(f"\nFound {len(prices_caches)} cached room-prices requests.")
    for idx, cached in enumerate(prices_caches):
        data = json.loads(cached.response_data)
        # Xem cấu trúc room-prices
        if isinstance(data, dict):
            print(f"\n--- Cache room-prices #{idx} ---")
            print("Root keys:", list(data.keys()))
            # Thử lấy roomGroups hoặc rooms
            groups = data.get("roomGroups", [])
            if groups:
                g = groups[0]
                print("Group keys:", list(g.keys()))
                rooms = g.get("rooms", [])
                if rooms:
                    r = rooms[0]
                    print("Room keys:", list(r.keys()))
                    print("images:", r.get("images"))
finally:
    db.close()
