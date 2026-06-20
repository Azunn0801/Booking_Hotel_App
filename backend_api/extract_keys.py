import requests
import json
import os

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

def fetch_details_others():
    url = "https://agoda-com.p.rapidapi.com/hotels/details-others"
    qs = {"propertyId":"9062231","checkinDate":"2026-06-16","checkoutDate":"2026-06-17","language":"vi-vn","currency":"VND","room":"2","adult":"2","childAges":"0,12,13,17"}
    res = requests.get(url, headers=headers, params=qs).json()
    with open('sample_details-others.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    return get_keys(res)

def fetch_room_prices():
    url = "https://agoda-com.p.rapidapi.com/hotels/room-prices"
    qs = {"propertyId":"9062231","checkinDate":"2026-06-17","checkoutDate":"2026-06-18","language":"vi-vn","currency":"VND","room":"-1","adult":"2","childAges":"0,12,13,17"}
    res = requests.get(url, headers=headers, params=qs).json()
    with open('sample_room-prices.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    return get_keys(res)

print("Fetching details-others...")
do_keys = fetch_details_others()
print("Fetching room-prices...")
rp_keys = fetch_room_prices()

# Analyze details
with open('sample_details.json', encoding='utf-8') as f:
    details_data = json.load(f)
    try:
        details_content = details_data['data']['propertyDetailsSearch']['propertyDetails'][0]['contentDetail']
        details_keys = get_keys(details_content)
    except:
        details_keys = {}

# Analyze search
with open('sample_search-overnight.json', encoding='utf-8') as f:
    search_data = json.load(f)
    try:
        search_keys = get_keys(search_data['data']['citySearch'])
    except:
        search_keys = {}

result = {
    "Search Overnight": search_keys,
    "Property Details": details_keys,
    "Details Others": do_keys,
    "Room Prices": rp_keys
}

with open('api_schema_keys.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("Keys extracted to api_schema_keys.json")
