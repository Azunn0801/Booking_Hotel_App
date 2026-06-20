import requests
import json
import time

headers = {
	"x-rapidapi-key": "7ac8e7f4aamshe3afd8116a3789dp118aa9jsnf974be0679d4",
	"x-rapidapi-host": "agoda-com.p.rapidapi.com",
	"Content-Type": "application/json"
}

def get_keys(obj):
    if isinstance(obj, dict):
        return {k: get_keys(v) for k, v in obj.items() if v is not None and v != [] and v != {}}
    elif isinstance(obj, list) and len(obj) > 0:
        return [get_keys(obj[0])]
    else:
        return type(obj).__name__

def fetch_api(endpoint, qs):
    url = f"https://agoda-com.p.rapidapi.com{endpoint}"
    print(f"Fetching {endpoint}...")
    try:
        res = requests.get(url, headers=headers, params=qs).json()
        with open(f"sample_{endpoint.replace('/', '_')}.json", "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        return get_keys(res)
    except Exception as e:
        print(f"Error on {endpoint}: {e}")
        return {"error": str(e)}

endpoints = [
    ("/hotels/auto-complete", {"query": "Vũng Tàu", "language": "vi-vn"}),
    ("/hotels/search-overnight", {"id": "1_17190", "checkinDate": "2026-06-20", "checkoutDate": "2026-06-21", "room": "1", "adult": "2", "limit": "5", "language": "vi-vn"}),
    ("/hotels/search-day-use", {"id": "1_17190", "checkinDate": "2026-06-20", "time": "10:00", "room": "1", "adult": "2", "limit": "5", "language": "vi-vn"}),
    ("/hotels/details", {"propertyId": "9062231", "language": "vi-vn"}),
    ("/hotels/details-others", {"propertyId": "9062231", "checkinDate": "2026-06-20", "checkoutDate": "2026-06-21", "language": "vi-vn", "currency": "VND", "room": "1", "adult": "2"}),
    ("/hotels/room-prices", {"propertyId": "9062231", "checkinDate": "2026-06-20", "checkoutDate": "2026-06-21", "language": "vi-vn", "currency": "VND", "room": "1", "adult": "2"}),
    ("/hotels/room-grid", {"propertyId": "9062231", "checkinDate": "2026-06-20", "checkoutDate": "2026-06-21", "language": "vi-vn", "currency": "VND", "room": "1", "adult": "2"}),
    ("/hotels/reviews", {"propertyId": "9062231", "reviewSources": "-1", "sort": "7", "page": "1", "limit": "10", "language": "vi-vn"})
]

results = {}
for ep, qs in endpoints:
    results[ep] = fetch_api(ep, qs)
    time.sleep(1)

with open("all_api_schema_keys.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("Finished extracting all 8 schemas to all_api_schema_keys.json")
