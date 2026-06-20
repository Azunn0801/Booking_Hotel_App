import json, requests

url = 'https://agoda-com.p.rapidapi.com/hotels/search-overnight'
headers = {
    'x-rapidapi-key': '7ac8e7f4aamshe3afd8116a3789dp118aa9jsnf974be0679d4',
    'x-rapidapi-host': 'agoda-com.p.rapidapi.com',
    'Content-Type': 'application/json'
}
res1 = requests.get(url, headers=headers, params={
    'id': '1_17190',
    'checkinDate': '2026-06-16',
    'checkoutDate': '2026-06-17',
    'room': '1',
    'adult': '2'
})
data = res1.json().get('data', {}).get('citySearch', {})
mgr = data.get('aggregation', {}).get('matrixGroupResults', [])

res = []
for g in mgr:
    group = g.get('matrixGroup')
    items = []
    for i in g.get('matrixItemResults', [])[:15]:
        items.append({
            'name': i.get('name'), 
            'id': i.get('id'), 
            'filterKey': i.get('filterKey'),
            'filterRequestType': i.get('filterRequestType')
        })
    res.append({'group': group, 'items': items})

with open('filters.json', 'w', encoding='utf-8') as f:
    json.dump(res, f, indent=2, ensure_ascii=False)
