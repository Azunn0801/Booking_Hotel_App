import json

def inspect_grid():
    try:
        with open('sample__hotels_room-grid.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        groups = data.get("roomGroups", [])
        print(f"Room Groups in grid: {len(groups)}")
        if groups:
            g = groups[0]
            print("Group keys:", list(g.keys()))
            rooms = g.get("rooms", [])
            print(f"Rooms in first group: {len(rooms)}")
            if rooms:
                r = rooms[0]
                print("Room keys:", list(r.keys()))
                # Tìm kiếm bất kỳ trường nào liên quan đến ảnh (image, photo, url)
                for key in r.keys():
                    if 'image' in key.lower() or 'photo' in key.lower() or 'url' in key.lower() or 'pic' in key.lower():
                        print(f"  Found matching key: {key} = {r[key]}")
                # Kiểm tra benefits
                print("benefits:", r.get("benefits"))
    except Exception as e:
        print("Error grid:", e)

def inspect_prices():
    try:
        with open('sample__hotels_room-prices.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Xem cấu trúc
        if isinstance(data, dict):
            # Nếu có roomGroups
            groups = data.get("roomGroups", [])
            print(f"Room Groups in prices: {len(groups)}")
            if groups:
                g = groups[0]
                rooms = g.get("rooms", [])
                if rooms:
                    r = rooms[0]
                    print("Prices Room keys:", list(r.keys()))
                    for key in r.keys():
                        if 'image' in key.lower() or 'photo' in key.lower() or 'url' in key.lower() or 'pic' in key.lower():
                            print(f"  Found matching key in prices room: {key} = {r[key]}")
    except Exception as e:
        print("Error prices:", e)

print("=== GRID ===")
inspect_grid()
print("\n=== PRICES ===")
inspect_prices()
