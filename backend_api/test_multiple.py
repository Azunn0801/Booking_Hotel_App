import requests
headers = {
    "x-rapidapi-key": "7ac8e7f4aamshe3afd8116a3789dp118aa9jsnf974be0679d4",
    "x-rapidapi-host": "agoda-com.p.rapidapi.com"
}
res = requests.get('https://agoda-com.p.rapidapi.com/hotels/details', headers=headers, params={'propertyId': '9062231,1026042', 'language': 'vi-vn'})
print(res.json())
