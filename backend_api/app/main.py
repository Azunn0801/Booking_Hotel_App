from fastapi import FastAPI, Depends, Query, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, database
from pydantic import BaseModel
from datetime import datetime, timedelta
from sqlalchemy import text
import os
import math
import requests
import hashlib
import re

# ==============================================================================
# Address Translation Helpers
# ==============================================================================
def strip_accents(text: str) -> str:
    if not text:
        return ""
    accents_map = {
        'a': 'áàảãạăắằẳẵặâấầẩẫậ',
        'A': 'ÁÀẢÃẠĂẮẰẰẴẶÂẤẦẨẪẬ',
        'd': 'đ',
        'D': 'Đ',
        'e': 'éèẻẽẹêếềểễệ',
        'E': 'ÉÈẺẼẸÊẾỀỂỄỆ',
        'i': 'íìỉĩị',
        'I': 'ÍÌỈĨỊ',
        'o': 'óòỏõọôốồổỗộơớờởỡợ',
        'O': 'ÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢ',
        'u': 'úùủũụưứừửữự',
        'U': 'ÚÙỦŨỤƯỨỪỬỮỰ',
        'y': 'ýỳỷỹỵ',
        'Y': 'ÝỲỶỸỴ'
    }
    for char, accented_chars in accents_map.items():
        for acc in accented_chars:
            text = text.replace(acc, char)
    return text

def translate_address_to_vietnamese(address: str) -> str:
    if not address:
        return ""
    
    address = re.sub(r'\bNo\.\s*(\d+)\b', r'Số \1', address, flags=re.IGNORECASE)
    address = re.sub(r'\bNo(\d+)\b', r'Số \1', address, flags=re.IGNORECASE)
    
    parts = [p.strip() for p in address.split(',')]
    translated_parts = []
    
    for part in parts:
        part_lower = part.lower()
        if part_lower in ['vietnam', 'viet nam']:
            part = 'Việt Nam'
            translated_parts.append(part)
            continue
        elif part_lower in ['ho chi minh city', 'ho chi minh', 'hcmc', 'tp. hcm', 'tp.hcm', 'thanh pho ho chi minh']:
            part = 'Thành phố Hồ Chí Minh'
            translated_parts.append(part)
            continue
        elif part_lower in ['ha noi', 'hanoi', 'ha noi city', 'thanh pho ha noi']:
            part = 'Hà Nội'
            translated_parts.append(part)
            continue
        elif part_lower in ['da nang', 'danang', 'da nang city', 'thanh pho da nang']:
            part = 'Đà Nẵng'
            translated_parts.append(part)
            continue
            
        # Dịch Ward không dấu
        ward_viet_match = re.search(r'^(Phuong|P\.?)\s+(.+)$', part, flags=re.IGNORECASE)
        if ward_viet_match and not re.match(r'^(Phường|Phuong)\b', ward_viet_match.group(2), flags=re.IGNORECASE):
            w_name = ward_viet_match.group(2).strip()
            if w_name.lower() == 'sai gon': w_name = 'Sài Gòn'
            part = f"Phường {w_name}"
            translated_parts.append(part)
            continue
            
        # Dịch District không dấu
        dist_viet_match = re.search(r'^(Quan|Q\.?)\s+(.+)$', part, flags=re.IGNORECASE)
        if dist_viet_match and not re.match(r'^(Quận|Quan)\b', dist_viet_match.group(2), flags=re.IGNORECASE):
            part = f"Quận {dist_viet_match.group(2).strip()}"
            translated_parts.append(part)
            continue

        # Check Street tiếng Anh
        street_match = re.search(r'^(.+?)\s+(Street|St\.?|street)$', part, flags=re.IGNORECASE)
        if street_match:
            street_name = street_match.group(1).strip()
            number_prefix_match = re.match(r'^(\d+(?:[/\-]\d+)*[a-zA-Z]?)\s+(.+)$', street_name)
            if number_prefix_match:
                num = number_prefix_match.group(1)
                name = number_prefix_match.group(2).strip()
                if not re.match(r'^(Đường|Duong)\b', name, flags=re.IGNORECASE):
                    part = f"{num} Đường {name}"
                else:
                    part = f"{num} {name}"
            else:
                if not re.match(r'^(Đường|Duong)\b', street_name, flags=re.IGNORECASE):
                    part = f"Đường {street_name}"
                else:
                    part = street_name
                
        # Check Ward tiếng Anh
        ward_match1 = re.search(r'^(.+?)\s+(Ward|ward)$', part, flags=re.IGNORECASE)
        ward_match2 = re.search(r'^(Ward|ward)\s+(.+)$', part, flags=re.IGNORECASE)
        if ward_match1:
            ward_name = ward_match1.group(1).strip()
            if not re.match(r'^(Phường|Phuong)\b', ward_name, flags=re.IGNORECASE):
                part = f"Phường {ward_name}"
            else:
                part = ward_name
        elif ward_match2:
            ward_num = ward_match2.group(2).strip()
            if not re.match(r'^(Phường|Phuong)\b', ward_num, flags=re.IGNORECASE):
                part = f"Phường {ward_num}"
            else:
                part = ward_num
            
        # Check District tiếng Anh
        dist_match1 = re.search(r'^(.+?)\s+(District|district|Dist\.?)$', part, flags=re.IGNORECASE)
        dist_match2 = re.search(r'^(District|district|Dist\.?)\s+(.+)$', part, flags=re.IGNORECASE)
        if dist_match1:
            dist_name = dist_match1.group(1).strip()
            if not re.match(r'^(Quận|Quan|Huyện|Huyen)\b', dist_name, flags=re.IGNORECASE):
                part = f"Quận {dist_name}"
            else:
                part = dist_name
        elif dist_match2:
            dist_num = dist_match2.group(2).strip()
            if not re.match(r'^(Quận|Quan|Huyện|Huyen)\b', dist_num, flags=re.IGNORECASE):
                part = f"Quận {dist_num}"
            else:
                part = dist_num
            
        translated_parts.append(part)
        
    final_parts = []
    for p in translated_parts:
        if p.lower() == 'sai gon':
            p = 'Sài Gòn'
            
        if p not in final_parts:
            p_norm = strip_accents(p).lower()
            if 'ho chi minh' in p_norm:
                if any('thanh pho ho chi minh' in strip_accents(x).lower() for x in final_parts):
                    continue
                if 'thanh pho' in p_norm:
                    for i, x in enumerate(final_parts):
                        if strip_accents(x).lower() == 'ho chi minh':
                            final_parts[i] = 'Thành phố Hồ Chí Minh'
                            break
                    else:
                        final_parts.append(p)
                    continue
            final_parts.append(p)
            
    if 'Việt Nam' in final_parts:
        final_parts.remove('Việt Nam')
        final_parts.append('Việt Nam')
        
    return ", ".join(final_parts)

def clean_street_address(street: str, area: str, city: str, country: str) -> str:
    translated_street = translate_address_to_vietnamese(street)
    
    parts = [p.strip() for p in translated_street.split(',')]
    clean_parts = []
    
    def normalize(s):
        if not s: return ""
        s = strip_accents(s).lower()
        s = s.replace('thanh pho', 'tp').replace('tp.', 'tp')
        s = s.replace('district', 'quan').replace('dist', 'quan')
        s = s.replace('ward', 'phuong')
        return "".join(s.split())

    norm_area = normalize(area)
    norm_city = normalize(city)
    norm_country = normalize(country)
    
    for part in parts:
        norm_part = normalize(part)
        if not norm_part:
            continue
            
        if norm_part == norm_area or norm_part == norm_city or norm_part == norm_country:
            continue
            
        part_clean_for_street_check = strip_accents(part).lower()
        is_street_or_road = any(x in part_clean_for_street_check for x in ['duong', 'pho', 'street', 'road'])
        if 'thanh pho' in part_clean_for_street_check:
            is_street_or_road = False
            
        if norm_city and (norm_part in norm_city or norm_city in norm_part) and not is_street_or_road:
            continue
        if norm_area and (norm_part in norm_area or norm_area in norm_part) and not is_street_or_road:
            continue
            
        clean_parts.append(part)
        
    return ", ".join(clean_parts)

# ==============================================================================
# RapidAPI Configuration
# ==============================================================================
# RapidAPI Configuration
# ==============================================================================
RAPIDAPI_KEY = "c5bd6f0f57msh276a40059613ad6p1f7db1jsn1aab83e37b9b"
RAPIDAPI_HOST = "agoda-com.p.rapidapi.com"
RAPIDAPI_BASE = f"https://{RAPIDAPI_HOST}"

import json

def rapidapi_get(endpoint: str, params: dict = None) -> dict:
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
        "Content-Type": "application/json"
    }
    if params is None:
        params = {}
    if endpoint in ["/hotels/search-overnight", "/hotels/room-prices", "/hotels/search-day-use", "/hotels/details-others"]:
        if "currency" not in params:
            params["currency"] = "VND"
            
    params_hash = None
    cache_file = None
    try:
        # Check cache from file
        params_hash = hashlib.md5(json.dumps(params, sort_keys=True).encode('utf-8')).hexdigest()
        cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        # Use endpoint name and params_hash for file name, replace slashes
        safe_endpoint = endpoint.strip('/').replace('/', '_')
        cache_file = os.path.join(cache_dir, f"{safe_endpoint}_{params_hash}.json")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            # Check TTL
            expires_at_str = cache_data.get('expires_at')
            if expires_at_str:
                expires_at = datetime.fromisoformat(expires_at_str)
                if expires_at > datetime.utcnow():
                    return cache_data.get('response_data')
            # Cache expired, remove file
            try:
                os.remove(cache_file)
            except Exception:
                pass
    except Exception:
        params_hash = None

    try:
        url = f"{RAPIDAPI_BASE}{endpoint}"
        response = requests.get(url, headers=headers, params=params, timeout=30)
        data = response.json()
        
        # Save cache to file if valid data received
        if cache_file and data and (not isinstance(data, dict) or not data.get("message", "").startswith("You have exceeded")):
            is_cacheable = False
            if isinstance(data, dict):
                CACHEABLE_KEYS = {"data", "places", "comments", "roomGroups", "type", "resultStatus", "AllCurrencyList", "children"}
                if any(k in data for k in CACHEABLE_KEYS):
                    is_cacheable = True
            elif isinstance(data, list):
                is_cacheable = True
                
            if is_cacheable:
                try:
                    if endpoint in ["/hotels/search-overnight", "/hotels/room-prices"]:
                        ttl = timedelta(hours=6)
                    else:
                        ttl = timedelta(hours=24)
                    
                    cache_content = {
                        'response_data': data,
                        'expires_at': (datetime.utcnow() + ttl).isoformat()
                    }
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(cache_content, f)
                except Exception:
                    pass

                    
        return data
    except Exception as e:
        return {"error": str(e)}

# ==============================================================================
# App Setup
# ==============================================================================
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Agoda Clone API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def ignore_map_and_devtools_logs(request: Request, call_next):
    path = request.url.path
    if path.endswith(".map") or "com.chrome.devtools.json" in path:
        return Response(status_code=204)
    return await call_next(request)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Trả về 204 để tránh 404 favicon trong console."""
    return Response(status_code=204)

WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "web_platform")
templates = Jinja2Templates(directory=os.path.join(WEB_DIR, "templates"))

# Fix: Prevent Jinja2 from parsing JS/CSS/JSON syntax
templates.env.block_start_string = '<%'
templates.env.block_end_string = '%>'
templates.env.variable_start_string = '<%='
templates.env.variable_end_string = '%>'
templates.env.comment_start_string = '<%#'
templates.env.comment_end_string = '%>'

# Custom Jinja2 filter
def default_filter(value, default_value):
    return value if value else default_value

templates.env.filters['default'] = default_filter

app.mount("/static", StaticFiles(directory=os.path.join(WEB_DIR, "static")), name="static")
app.mount("/resources_web", StaticFiles(directory=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources_web")), name="resources_web")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None
    try:
        user_id = int(user_id)
        user = db.query(models.User).filter(models.User.id == user_id).first()
        return user
    except:
        return None

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# ==============================================================================
# Pydantic Models
# ==============================================================================
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class BookingCreate(BaseModel):
    user_id: int
    property_id: str
    property_name: str
    property_type: str = "hotel"
    property_image: str = ""
    checkin_date: str
    checkin_time: Optional[str] = None
    checkout_date: str
    total_price: float
    original_price: float = 0
    discount_amount: float = 0
    promotion_code: Optional[str] = None

class ProfileUpdate(BaseModel):
    full_name: str

class PromoApply(BaseModel):
    code: str
    total_price: float

class PromoClaim(BaseModel):
    user_id: int
    code: str

# Schema for creating a property in YCS
class PropertyCreate(BaseModel):
    name: str
    property_type: str
    city: str
    address: str
    price: float
    description: Optional[str] = None
    image_url: Optional[str] = None

def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_date_format(date_str: str) -> bool:
    """Validate date string is in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# ==============================================================================
# DEBUG ENDPOINT
# ==============================================================================
@app.get("/debug/rapidapi")
def debug_rapidapi(id: str = "1_2758", checkinDate: str = "2026-06-01", checkoutDate: str = "2026-06-02"):
    params = {"id": id, "checkinDate": checkinDate, "checkoutDate": checkoutDate, "sort": "Ranking,Desc"}
    data = rapidapi_get("/hotels/search-overnight", params)
    if not data.get("data"):
        return {"status": "no_data", "raw_keys": list(data.keys())}
    city_search = data["data"].get("citySearch")
    if not city_search:
        return {"status": "no_citySearch", "data_keys": list(data["data"].keys())}
    # properties nằm trực tiếp trong citySearch, KHÔNG phải trong searchResult
    properties = city_search.get("properties", [])
    if not properties:
        return {"status": "no_properties", "citySearch_keys": list(city_search.keys())}
    p = properties[0]
    content = p.get("content", {})
    info = content.get("informationSummary", {})
    pricing = p.get("pricing", {})
    
    # Extract price with deep debug
    price = 0
    orig = 0
    disc = 0
    offers = pricing.get("offers", [])
    debug_info = {}
    debug_info["offers_len"] = len(offers)
    if offers:
        offer0 = offers[0]
        debug_info["offer0_keys"] = list(offer0.keys())
        ro = offer0.get("roomOffers", [])
        debug_info["ro_len"] = len(ro)
        if ro:
            ro0 = ro[0]
            debug_info["ro0_keys"] = list(ro0.keys())
            # Dump raw ro0 to see structure
            import json
            try:
                debug_info["ro0_raw"] = json.dumps(ro0, default=str)[:2000]
            except:
                debug_info["ro0_raw"] = str(ro0)[:2000]
            
            # Try to find pricing in ro0 or inside room
            pl = ro0.get("pricing", [])
            if not pl:
                room_inside = ro0.get("room", {})
                if isinstance(room_inside, dict):
                    pl = room_inside.get("pricing", [])
            debug_info["pl_len"] = len(pl)
            if pl:
                pl0 = pl[0]
                debug_info["pl0_keys"] = list(pl0.keys()) if isinstance(pl0, dict) else str(type(pl0))
                pi = pl0.get("price", {}) if isinstance(pl0, dict) else {}
                pn = pi.get("perRoomPerNight", {}) if isinstance(pl0, dict) else {}
                exc = pn.get("exclusive", {}) if isinstance(pl0, dict) else {}
                price = exc.get("display", 0)
                orig = exc.get("crossedOutPrice", 0)
                disc = pi.get("totalDiscount", 0)
    
    return {
        "status": "ok",
        "total": len(properties),
        "first_id": p.get("propertyId"),
        "first_name": info.get("localeName", info.get("defaultName")),
        "has_pricing": bool(pricing),
        "price": price,
        "originalPrice": orig,
        "discountPercent": disc,
        "debug": debug_info,
    }

# ==============================================================================
# PAGE ROUTES (web_platform)
# ==============================================================================
@app.get("/")
def page_home(request: Request, user=Depends(get_current_user_from_cookie)):
    return templates.TemplateResponse(request=request, name="index.html", context={"user": user})

@app.get("/search")
def page_search(request: Request, user=Depends(get_current_user_from_cookie)):
    return templates.TemplateResponse(request=request, name="search.html", context={"user": user})

@app.get("/deals")
def page_deals(request: Request, user=Depends(get_current_user_from_cookie)):
    return templates.TemplateResponse(request=request, name="deals.html", context={"user": user})

@app.get("/hotel/{hotel_id}")
def page_hotel_detail(request: Request, hotel_id: str, user=Depends(get_current_user_from_cookie)):
    return templates.TemplateResponse(request=request, name="detail.html", context={"request": request, "hotel_id": hotel_id, "user": user})

@app.get("/login")
def page_login(request: Request, next: Optional[str] = "/"):
    return templates.TemplateResponse(request=request, name="login.html", context={"next": next})

@app.get("/register")
def page_register(request: Request, next: Optional[str] = "/"):
    return templates.TemplateResponse(request=request, name="register.html", context={"next": next})

@app.get("/profile")
def page_profile(request: Request, user=Depends(get_current_user_from_cookie)):
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login?next=/profile")
    return templates.TemplateResponse(request=request, name="profile.html", context={"user": user})

@app.get("/list-property")
def page_list_property(request: Request, user=Depends(get_current_user_from_cookie)):
    return templates.TemplateResponse(request=request, name="list_property.html", context={"user": user})

@app.get("/list-property/register")
def page_list_property_register(request: Request, user=Depends(get_current_user_from_cookie)):
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login?next=/list-property/register")
    return templates.TemplateResponse(request=request, name="list_property_form.html", context={"user": user})

@app.get("/agodacash")
def page_agodacash(request: Request, user=Depends(get_current_user_from_cookie)):
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login?next=/agodacash")
    return templates.TemplateResponse(request=request, name="agodacash.html", context={"user": user})

@app.get("/cashback")
def page_cashback(request: Request, user=Depends(get_current_user_from_cookie)):
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login?next=/cashback")
    return templates.TemplateResponse(request=request, name="cashback.html", context={"user": user})

@app.get("/inbox")
def page_inbox(request: Request, user=Depends(get_current_user_from_cookie)):
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login?next=/inbox")
    return templates.TemplateResponse(request=request, name="inbox.html", context={"user": user})

@app.get("/pointsmax")
def page_pointsmax(request: Request, user=Depends(get_current_user_from_cookie)):
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login?next=/pointsmax")
    return templates.TemplateResponse(request=request, name="pointsmax.html", context={"user": user})

@app.get("/reviews")
def page_reviews(request: Request, user=Depends(get_current_user_from_cookie)):
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login?next=/reviews")
    return templates.TemplateResponse(request=request, name="reviews.html", context={"user": user})

@app.get("/reviews/submit/{booking_id}")
def page_submit_review(request: Request, booking_id: int, user=Depends(get_current_user_from_cookie), db: Session = Depends(get_db)):
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=f"/login?next=/reviews/submit/{booking_id}")
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return templates.TemplateResponse(request=request, name="submit.html", context={"user": user, "booking": booking})

@app.get("/vip")
def page_vip(request: Request, user=Depends(get_current_user_from_cookie)):
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login?next=/vip")
    return templates.TemplateResponse(request=request, name="vip.html", context={"user": user})

@app.get("/trips")
def page_trips(request: Request, user=Depends(get_current_user_from_cookie)):
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login?next=/trips")
    return templates.TemplateResponse(request=request, name="trips.html", context={"user": user})

@app.get("/bookings")
def page_bookings_list(request: Request, user=Depends(get_current_user_from_cookie)):
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login?next=/bookings")
    return templates.TemplateResponse(request=request, name="bookings_list.html", context={"user": user})

@app.get("/booking/{booking_id}")
def page_booking_detail(request: Request, booking_id: int, user=Depends(get_current_user_from_cookie), db: Session = Depends(get_db)):
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=f"/login?next=/booking/{booking_id}")
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return templates.TemplateResponse(request=request, name="booking_detail.html", context={"user": user, "booking": booking})

# ==============================================================================
# YCS PARTNER PORTAL ENDPOINTS
# ==============================================================================

@app.get("/ycs")
def page_ycs_portal(request: Request, user=Depends(get_current_user_from_cookie), db: Session = Depends(get_db)):
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login?next=/ycs")
    
    # Query properties owned by this user
    props = db.query(models.Property).filter(models.Property.owner_id == user.id).all()
    
    return templates.TemplateResponse(
        request=request, 
        name="ycs_portal.html", 
        context={"request": request, "user": user, "properties": props}
    )

@app.get("/ycs/property/{property_id}")
def page_ycs_dashboard(request: Request, property_id: str, user=Depends(get_current_user_from_cookie), db: Session = Depends(get_db)):
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=f"/login?next=/ycs/property/{property_id}")
        
    prop = db.query(models.Property).filter(
        models.Property.id == property_id,
        models.Property.owner_id == user.id
    ).first()
    
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found or access denied")
        
    all_props = db.query(models.Property).filter(models.Property.owner_id == user.id).all()
    
    return templates.TemplateResponse(
        request=request, 
        name="ycs_dashboard.html", 
        context={"request": request, "user": user, "property": prop, "all_properties": all_props}
    )

@app.post("/api/host/properties")
def create_host_property(prop_data: PropertyCreate, user=Depends(get_current_user_from_cookie), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    import uuid
    prop_id = f"host_{uuid.uuid4().hex[:8]}"
    
    img_url = prop_data.image_url.strip() if prop_data.image_url else ""
    if not img_url:
        if prop_data.property_type == "villa":
            img_url = "https://images.unsplash.com/photo-1580587771525-78b9dba3b914"
        elif prop_data.property_type == "apartment":
            img_url = "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688"
        else:
            img_url = "https://images.unsplash.com/photo-1566073771259-6a8506099945"
            
    new_prop = models.Property(
        id=prop_id,
        owner_id=user.id,
        name=prop_data.name,
        property_type=prop_data.property_type,
        city=prop_data.city,
        address=prop_data.address,
        description=prop_data.description,
        price=prop_data.price,
        image_url=img_url,
        star_rating=4.0,
        status="Approved"
    )
    db.add(new_prop)
    db.commit()
    return {"status": "success", "property_id": prop_id, "message": "Property registered successfully"}

@app.get("/api/host/properties")
def get_host_properties(user=Depends(get_current_user_from_cookie), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    props = db.query(models.Property).filter(models.Property.owner_id == user.id).all()
    return props

@app.get("/api/host/properties/{property_id}/bookings")
def get_host_property_bookings(property_id: str, user=Depends(get_current_user_from_cookie), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    prop = db.query(models.Property).filter(models.Property.id == property_id, models.Property.owner_id == user.id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
        
    bookings = db.query(models.Booking).filter(models.Booking.property_id == property_id).order_by(models.Booking.id.desc()).all()
    return [{
        "id": b.id,
        "user_name": db.query(models.User).filter(models.User.id == b.user_id).first().full_name if db.query(models.User).filter(models.User.id == b.user_id).first() else "Khách vãng lai",
        "checkin_date": b.checkin_date,
        "checkout_date": b.checkout_date,
        "total_price": b.total_price,
        "status": b.status,
        "created_at": b.created_at.strftime("%Y-%m-%d %H:%M")
    } for b in bookings]

@app.get("/api/host/properties/{property_id}/analytics")
def get_host_property_analytics(property_id: str, user=Depends(get_current_user_from_cookie), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    prop = db.query(models.Property).filter(models.Property.id == property_id, models.Property.owner_id == user.id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
        
    bookings = db.query(models.Booking).filter(
        models.Booking.property_id == property_id,
        models.Booking.status != "cancelled"
    ).all()
    
    total_bookings = len(bookings)
    mtd_revenue = sum(b.total_price for b in bookings)
    
    occupancy_rate = 65.0
    if total_bookings > 0:
        occupancy_rate = min(35.0 + (total_bookings * 10), 95.0)
        
    labels = ["Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6"]
    revenue_data = [0.0] * 6
    
    if mtd_revenue > 0:
        revenue_data = [
            round(mtd_revenue * 0.15, 2),
            round(mtd_revenue * 0.20, 2),
            round(mtd_revenue * 0.12, 2),
            round(mtd_revenue * 0.18, 2),
            round(mtd_revenue * 0.25, 2),
            round(mtd_revenue * 0.10, 2)
        ]
        revenue_data[5] = round(mtd_revenue, 2)
    else:
        revenue_data = [5000000.0, 7500000.0, 6200000.0, 9800000.0, 12000000.0, 0.0]
        
    return {
        "mtd_revenue": mtd_revenue,
        "total_bookings": total_bookings,
        "occupancy_rate": occupancy_rate,
        "chart": {
            "labels": labels,
            "data": revenue_data
        }
    }

# ==============================================================================
# LEGACY ENDPOINTS (for web_platform/app.js compatibility)
# ==============================================================================

@app.get("/hotels/auto-complete")
def hotels_auto_complete(q: str = Query(...), language: str = "vi-vn"):
    data = rapidapi_get("/hotels/auto-complete", {"query": q, "language": language})
    places = data.get("places", [])
    results = []
    for p in places:
        city = p.get("city")
        results.append({
            "id": p.get("id"),
            "name": p.get("name"),
            "type": p.get("typeName", ""),
            "searchType": p.get("searchType", 1),
            "city": city.get("name") if city else p.get("name"),
            "city_id": city.get("id") if city else p.get("id"),
            "country": p.get("country", {}).get("name", ""),
            "latitude": p.get("latitude", 0),
            "longitude": p.get("longitude", 0),
            "activeHotels": p.get("activeHotels", 0),
            "state_id": p.get("state", {}).get("id", 0) if isinstance(p.get("state"), dict) else 0,
            "state_name": p.get("state", {}).get("name", "") if isinstance(p.get("state"), dict) else ""
        })

    # FALLBACK: Nếu Agoda bị nghẽn (không trả về kết quả), tìm kiếm trong cơ sở dữ liệu nội bộ
    if not results:
        db = database.SessionLocal()
        try:
            import unicodedata
            def remove_accents(input_str):
                if not input_str:
                    return ""
                nfkd_form = unicodedata.normalize('NFKD', str(input_str))
                return u"".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()
                
            query_unaccented = remove_accents(q)
            
            # Lấy toàn bộ chỗ nghỉ đã duyệt và lọc bằng Python để hỗ trợ Tiếng Việt không dấu
            all_props = db.query(models.Property).filter(models.Property.status == "Approved").all()
            
            seen_cities = set()
            for prop in all_props:
                city_unaccented = remove_accents(prop.city)
                name_unaccented = remove_accents(prop.name)
                
                # Nếu từ khóa khớp với tên thành phố hoặc tên khách sạn
                if query_unaccented in city_unaccented or query_unaccented in name_unaccented:
                    # Gợi ý thành phố
                    if query_unaccented in city_unaccented and prop.city not in seen_cities:
                        results.append({
                            "id": "1_" + str(len(seen_cities) + 9999),
                            "name": prop.city,
                            "type": "City",
                            "city": prop.city,
                            "city_id": "1_" + str(len(seen_cities) + 9999),
                            "country": "Việt Nam"
                        })
                        seen_cities.add(prop.city)
                    
                    # Nếu nó khớp cụ thể tên khách sạn, gợi ý tên khách sạn đó luôn
                    if query_unaccented in name_unaccented:
                        results.append({
                            "id": prop.id,
                            "name": prop.name,
                            "type": "Hotel",
                            "city": prop.city,
                            "city_id": "1_9999",
                            "country": "Việt Nam"
                        })
                    
                    # Giới hạn 10 kết quả gợi ý
                    if len(results) >= 10:
                        break
        finally:
            db.close()

    return results

@app.get("/hotels/search-overnight")
def search_overnight_legacy(
    id: str = Query(...),
    checkinDate: str = Query(None),
    checkoutDate: str = Query(None),
    starRating: Optional[str] = None,
    prices: Optional[str] = None,
    sort: str = "Ranking,Desc",
    limit: int = 10,
    accommodationType: Optional[str] = None
):
    """Legacy endpoint - returns transformed data for web_platform"""
    params = {
        "id": id,
        "checkinDate": checkinDate or "2026-06-01",
        "checkoutDate": checkoutDate or "2026-06-02",
        "sort": sort,
    }
    if starRating:
        params["starRating"] = starRating
    if accommodationType:
        params["accommodationType"] = accommodationType

    data = rapidapi_get("/hotels/search-overnight", params)

    if not data.get("data"):
        return []

    city_search = data["data"].get("citySearch", {})
    properties = city_search.get("properties", [])

    results = []
    for p in properties:
        content = p.get("content", {})
        info = content.get("informationSummary", {})
        reviews = content.get("reviews", {}).get("cumulative", {})
        pricing = p.get("pricing", {})
        images = content.get("images", {}).get("hotelImages", [])

        image_url = ""
        for img in images:
            urls = img.get("urls", [])
            if urls:
                url_val = urls[0].get("value", "")
                if url_val:
                    image_url = "https:" + url_val if url_val.startswith("//") else url_val
                    break

        price = 0
        original_price = 0
        discount_percent = 0
        offers = pricing.get("offers", [])
        if offers:
            room_offers = offers[0].get("roomOffers", [])
            if room_offers:
                ro0 = room_offers[0]
                pricing_list = ro0.get("pricing", [])
                if not pricing_list:
                    room_data = ro0.get("room", {})
                    if isinstance(room_data, dict):
                        pricing_list = room_data.get("pricing", [])
                if pricing_list:
                    price_info = pricing_list[0].get("price", {})
                    per_night = price_info.get("perRoomPerNight", {})
                    exclusive = per_night.get("exclusive", {})
                    price = exclusive.get("display", 0)
                    original_price = exclusive.get("crossedOutPrice", 0)
                    discount_percent = price_info.get("totalDiscount", 0)

        score = reviews.get("score", 0)
        review_count = reviews.get("reviewCount", 0)
        geo = info.get("geoInfo", {})
        address_info = info.get("address", {})
        area = address_info.get("area", {})
        accommodation = info.get("accommodation", {})

        # Price filter (trước khi thêm vào results)
        if prices:
            try:
                parts = [float(x) for x in prices.split(",") if x.strip()]
                if len(parts) >= 2:
                    if price < parts[0] or price > parts[1]:
                        continue
                elif len(parts) == 1:
                    if price < parts[0]:
                        continue
            except:
                pass

        results.append({
            "id": str(p.get("propertyId", "")),
            "name": info.get("localeName", info.get("defaultName", "")),
            "address": area.get("name", ""),
            "city": address_info.get("city", {}).get("name", ""),
            "city_id": str(address_info.get("city", {}).get("id", "")),
            "star_rating": info.get("rating", 0),
            "image_url": image_url,
            "is_available": pricing.get("isAvailable", False),
            "price": price,
            "original_price": original_price,
            "discount_percent": discount_percent,
            "score": score,
            "review_count": review_count,
            "is_preferred": score >= 8.0,
            "latitude": geo.get("latitude", 0),
            "longitude": geo.get("longitude", 0),
            "property_type": accommodation.get("accommodationName", "Hotel")
        })

    # Sort TRƯỚC khi slice để kết quả chính xác
    if sort == "Price,Asc":
        # Đưa price=0 (không có giá) xuống cuối danh sách
        results.sort(key=lambda x: (x["price"] == 0, x["price"]))
    elif sort == "Price,Desc":
        results.sort(key=lambda x: x["price"], reverse=True)
    elif sort in ["Ranking,Desc", "Rating,Desc", "Score,Desc", "Review,Desc"]:
        results.sort(key=lambda x: x["score"], reverse=True)

    return results[:limit]

@app.get("/hotels/details")
def get_hotel_details_legacy(hotel_id: int):
    data = rapidapi_get("/hotels/details", {"propertyId": str(hotel_id), "language": "vi-vn"})
    if not data.get("data"):
        raise HTTPException(status_code=404, detail="Not found")
    details = data["data"].get("propertyDetailsSearch", {}).get("propertyDetails", [])
    if not details:
        raise HTTPException(status_code=404, detail="Not found")

    content = details[0].get("contentDetail", {})
    summary = content.get("contentSummary", {})
    geo = summary.get("geoInfo", {})

    return {
        "id": hotel_id,
        "name": summary.get("localeName", summary.get("defaultName", "")),
        "address": summary.get("address", {}).get("area", {}).get("name", ""),
        "star_rating": summary.get("rating", 0),
        "latitude": geo.get("latitude", 0),
        "longitude": geo.get("longitude", 0),
        "image_url": ""
    }

@app.get("/hotels/room-prices")
def get_room_prices_legacy(hotel_id: int, checkinDate: str = "2026-06-01", checkoutDate: str = "2026-06-02"):
    data = rapidapi_get("/hotels/room-prices", {"hotel_id": str(hotel_id), "checkinDate": checkinDate, "checkoutDate": checkoutDate})

    rooms = []
    if data.get("data"):
        # Parse room-prices response
        room_data = data["data"]
        if isinstance(room_data, dict):
            for key, val in room_data.items():
                if isinstance(val, list):
                    for r in val:
                        rooms.append({
                            "id": r.get("roomId", 0),
                            "room_name": r.get("roomName", "Room"),
                            "price": r.get("price", 0),
                            "original_price": r.get("originalPrice", 0),
                            "discount_percent": r.get("discountPercent", 0),
                            "amenities": r.get("amenities", ""),
                            "is_available": True
                        })

    # Fallback: use search-overnight pricing
    if not rooms:
        search_data = rapidapi_get("/hotels/search-overnight", {
            "id": f"1_{hotel_id}",
            "checkinDate": checkinDate,
            "checkoutDate": checkoutDate,
            "limit": "1"
        })
        if search_data.get("data"):
            props = search_data["data"].get("citySearch", {}).get("properties", [])
            if props:
                pricing = props[0].get("pricing", {})
                offers = pricing.get("offers", [])
                for offer in offers:
                    for ro in offer.get("roomOffers", []):
                        room = ro.get("room", {})
                        pricing_list = ro.get("pricing", [])
                        if not pricing_list and isinstance(room, dict):
                            pricing_list = room.get("pricing", [])
                        price = 0
                        orig = 0
                        if pricing_list:
                            p = pricing_list[0].get("price", {})
                            per_night = p.get("perRoomPerNight", {}).get("exclusive", {})
                            price = per_night.get("display", 0)
                            orig = per_night.get("crossedOutPrice", 0)

                        benefits = room.get("benefits", [])
                        amenities = ", ".join([b.get("description", "") for b in benefits]) if benefits else "WiFi"

                        rooms.append({
                            "id": int(str(hotel_id) + str(abs(hash(ro.get("uid", ""))))[:5]),
                            "room_name": f"Room (up to {room.get('occupancy', 2)} guests)",
                            "price": price,
                            "original_price": orig,
                            "discount_percent": int((1 - price/orig)*100) if orig > 0 else 0,
                            "amenities": amenities,
                            "is_available": True
                        })

    return rooms

@app.get("/hotels/recommend-by-location")
def recommend_by_location_legacy(
    latitude: float = Query(...),
    longitude: float = Query(...),
    limit: int = 6
):
    """Recommend hotels by location - finds the nearest major city based on coordinates.
    Sử dụng danh sách 11 thành phố lớn của Việt Nam, tính khoảng cách haversine
    để tìm thành phố gần nhất với vị trí người dùng.
    """
    cities = [
        {"id": "1_13170", "name": "Hồ Chí Minh", "lat": 10.785082, "lon": 106.676559},
        {"id": "1_2758",  "name": "Hà Nội",      "lat": 21.026668, "lon": 105.848808},
        {"id": "1_16440", "name": "Đà Nẵng",     "lat": 16.066599, "lon": 108.212242},
        {"id": "1_2679",  "name": "Nha Trang",   "lat": 12.244566, "lon": 109.195175},
        {"id": "1_17188", "name": "Phú Quốc",    "lat": 10.289585, "lon": 103.984222},
        {"id": "1_15932", "name": "Đà Lạt",      "lat": 11.945456, "lon": 108.443298},
        {"id": "1_16552", "name": "Hội An",       "lat": 15.881267, "lon": 108.327427},
        {"id": "1_16079", "name": "Cần Thơ",     "lat": 10.035633, "lon": 105.780665},
        {"id": "1_3738",  "name": "Huế",          "lat": 16.462755, "lon": 107.587395},
        {"id": "1_17190", "name": "Vũng Tàu",    "lat": 10.402391, "lon": 107.148628},
        {"id": "1_16264", "name": "Phan Thiết",  "lat": 10.923900, "lon": 108.105900},
    ]
    # Find nearest city based on distance
    nearest_city = min(cities, key=lambda c: haversine_distance(latitude, longitude, c["lat"], c["lon"]))
    city_id = nearest_city["id"]
    city_name = nearest_city["name"]

    # Dùng ngày động thay vì hardcoded để tránh kết quả lỗi thời
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    day_after = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")

    data = rapidapi_get("/hotels/search-overnight", {
        "id": city_id,
        "checkinDate": tomorrow,
        "checkoutDate": day_after,
        "sort": "Ranking,Desc",
    })

    if not data.get("data"):
        return {"city_id": city_id, "city_name": city_name, "results": []}

    properties = data["data"].get("citySearch", {}).get("properties", [])

    results = []
    for p in properties:
        content = p.get("content", {})
        info = content.get("informationSummary", {})
        reviews = content.get("reviews", {}).get("cumulative", {})
        pricing = p.get("pricing", {})
        images = content.get("images", {}).get("hotelImages", [])
        geo = info.get("geoInfo", {})

        if not geo.get("latitude") or not geo.get("longitude"):
            continue

        distance = haversine_distance(latitude, longitude, geo["latitude"], geo["longitude"])

        image_url = ""
        for img in images:
            urls = img.get("urls", [])
            if urls:
                val = urls[0].get("value", "")
                if val:
                    image_url = "https:" + val if val.startswith("//") else val
                    break

        price = 0
        orig = 0
        disc = 0
        offers = pricing.get("offers", [])
        if offers:
            ro = offers[0].get("roomOffers", [])
            if ro:
                ro0 = ro[0]
                pl = ro0.get("pricing", [])
                if not pl:
                    room_data = ro0.get("room", {})
                    if isinstance(room_data, dict):
                        pl = room_data.get("pricing", [])
                if pl:
                    pi = pl[0].get("price", {})
                    pn = pi.get("perRoomPerNight", {}).get("exclusive", {})
                    price = pn.get("display", 0)
                    orig = pn.get("crossedOutPrice", 0)
                    disc = pi.get("totalDiscount", 0)

        address_info = info.get("address", {})
        area = address_info.get("area", {})

        results.append({
            "id": str(p.get("propertyId", "")),
            "name": info.get("localeName", info.get("defaultName", "")),
            "address": area.get("name", ""),
            "city": address_info.get("city", {}).get("name", ""),
            "city_id": str(address_info.get("city", {}).get("id", "")),
            "star_rating": info.get("rating", 0),
            "image_url": image_url,
            "is_available": pricing.get("isAvailable", False),
            "price": price,
            "original_price": orig,
            "discount_percent": disc,
            "score": reviews.get("score", 0),
            "review_count": reviews.get("reviewCount", 0),
            "is_preferred": reviews.get("score", 0) >= 8.0,
            "latitude": geo["latitude"],
            "longitude": geo["longitude"],
            "distance": round(distance, 2)
        })

    results.sort(key=lambda x: x["distance"])
    return {
        "city_id": city_id,
        "city_name": city_name,
        "results": results[:limit]
    }

# ==============================================================================
# NEW API ENDPOINTS (for Android app)
# ==============================================================================

@app.get("/api/autocomplete")
def autocomplete(query: str = Query(...), language: str = "vi-vn"):
    data = rapidapi_get("/hotels/auto-complete", {"query": query, "language": language})
    places = data.get("places", [])
    results = []
    for p in places:
        city = p.get("city")
        results.append({
            "id": p.get("id"),
            "name": p.get("name"),
            "type": p.get("typeName", ""),
            "search_type": p.get("searchType", 1),
            "city_id": city.get("id") if city else None,
            "city_name": city.get("name") if city else None,
            "country_name": p.get("country", {}).get("name") if p.get("country") else None,
            "latitude": p.get("latitude", 0),
            "longitude": p.get("longitude", 0),
            "active_hotels": p.get("activeHotels", 0)
        })
    return results

@app.get("/api/properties/search")
def search_properties(
    request: Request,
    city_id: str = Query(...),
    checkin: str = Query(...),
    checkout: Optional[str] = Query(None),
    booking_type: str = "overnight",
    time: Optional[str] = None,
    room: int = 1,
    adult: int = 2,
    childAges: Optional[str] = None,
    property_type: Optional[str] = None,
    star_rating: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort: str = "Ranking,Desc",
    limit: int = 20,
    include_filters: bool = False,
    db: Session = Depends(get_db)
):
    if booking_type == "dayuse" and not time:
        time = "10:00" # Default time if not provided

    # Ensure city_id has 1_ prefix for city search
    if not str(city_id).startswith("1_") and "_" not in str(city_id):
        city_id = f"1_{city_id}"

    params = {
        "id": city_id,
        "checkinDate": checkin,
        "sort": sort,
        "language": "vi-vn",
        "room": str(room),
        "adult": str(adult)
    }
    
    if checkout and booking_type != "dayuse":
        params["checkoutDate"] = checkout
    if time and booking_type == "dayuse":
        params["time"] = time
    if childAges:
        params["childAges"] = childAges
    if limit > 0:
        params["limit"] = str(limit)

    acc_map = {"hotel": "34", "apartment": "29,120", "villa": "28,131"}
    if property_type and property_type in acc_map:
        if booking_type == "dayuse":
            params["propertyType"] = acc_map[property_type]
        else:
            params["accommodationType"] = acc_map[property_type]
            
    if star_rating:
        params["starRating"] = star_rating
        
    if min_price is not None or max_price is not None:
        if booking_type == "dayuse":
            params["prices"] = f"{int(min_price or 0)},{int(max_price or 99999999)}"
        else:
            if min_price is not None:
                params["minPrice"] = str(int(min_price))
            if max_price is not None:
                params["maxPrice"] = str(int(max_price))

    # Forward dynamic query params for filters
    known_params = {"city_id", "checkin", "checkout", "booking_type", "time", "room", "adult", "childAges", "property_type", "star_rating", "min_price", "max_price", "sort", "limit", "include_filters"}
    for key, value in request.query_params.items():
        if key not in known_params:
            params[key] = value

    endpoint = "/hotels/search-day-use" if booking_type == "dayuse" else "/hotels/search-overnight"
    
    # Query local properties matching the city
    CITY_ID_MAP = {
        "1_13170": ["ho chi minh", "hcm", "sài gòn", "sai gon"],
        "1_2758": ["ha noi", "hà nội"],
        "1_16440": ["da nang", "đà nẵng"],
        "1_2679": ["nha trang"],
        "1_17188": ["phu quoc", "phú quốc"],
        "1_15932": ["da lat", "đà lạt"],
        "1_16552": ["hoi an", "hội an"],
        "1_16079": ["can tho", "cần thơ"],
        "1_3738": ["hue", "huế"],
        "1_17190": ["vung tau", "vũng tàu"],
        "1_16264": ["phan thiet", "phan thiết"]
    }
    
    local_results = []
    try:
        import unicodedata
        def remove_accents(input_str):
            if not input_str:
                return ""
            nfkd_form = unicodedata.normalize('NFKD', str(input_str))
            return u"".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

        keywords = CITY_ID_MAP.get(str(city_id), [])
        unaccented_keywords = [remove_accents(kw) for kw in keywords]
        
        query = db.query(models.Property).filter(models.Property.status == "Approved")
        if property_type:
            query = query.filter(models.Property.property_type.ilike(property_type))
            
        all_props = query.all()
        
        local_props = []
        if keywords:
            for prop in all_props:
                city_unaccented = remove_accents(prop.city)
                addr_unaccented = remove_accents(prop.address)
                
                matched = False
                for kw in unaccented_keywords:
                    if kw in city_unaccented or kw in addr_unaccented:
                        matched = True
                        break
                
                if matched:
                    local_props.append(prop)
        else:
            local_props = all_props
        for lp in local_props:
            lp_price = lp.price
            local_results.append({
                "id": lp.id,
                "name": lp.name,
                "propertyType": lp.property_type,
                "propertyTypeName": lp.property_type.capitalize(),
                "address": lp.address,
                "city": lp.city,
                "starRating": lp.star_rating,
                "score": 9.2,
                "reviewCount": 12,
                "imageUrl": lp.image_url.split(",")[0] if lp.image_url else "https://images.unsplash.com/photo-1566073771259-6a8506099945",
                "price": lp_price,
                "originalPrice": lp_price * 1.2,
                "discountPercent": 20,
                "latitude": 10.402,
                "longitude": 107.148,
                "isPreferred": True,
                "isAvailable": True,
                "reviewQuote": "Tuyệt vời",
                "distanceDescription": "Gần trung tâm",
                
                # snake_case compatibility
                "property_type": lp.property_type,
                "property_type_name": lp.property_type.capitalize(),
                "star_rating": lp.star_rating,
                "review_count": 12,
                "image_url": lp.image_url.split(",")[0] if lp.image_url else "https://images.unsplash.com/photo-1566073771259-6a8506099945",
                "original_price": lp_price * 1.2,
                "discount_percent": 20,
                "is_preferred": True,
                "is_available": True,
                "review_quote": "Tuyệt vời",
                "distance_description": "Gần trung tâm"
            })
    except Exception as e:
        import traceback
        print(f"Error merging local search: {repr(e)}")
        print(traceback.format_exc().encode('ascii', 'ignore').decode('ascii'))

    data = rapidapi_get(endpoint, params)
    
    if "error" in data:
        print(f"RapidAPI Timeout/Error: {data['error']}")
        if not local_results:
            from fastapi import HTTPException
            raise HTTPException(status_code=502, detail="Máy chủ Agoda không phản hồi. Vui lòng thử lại sau.")
        return local_results

    if not data.get("data"):
        return local_results

    city_search = data["data"].get("citySearch") if booking_type != "dayuse" else data["data"]
    if not city_search:
        return local_results
        
    properties = city_search.get("properties", [])
    if not properties:
        return local_results
        
    results = []
    for p in properties:
        content = p.get("content") or {}
        info = content.get("informationSummary") or {}
        reviews_data = content.get("reviews") or {}
        reviews = reviews_data.get("cumulative") or {}
        pricing = p.get("pricing") or {}
        images_data = content.get("images") or {}
        images = images_data.get("hotelImages") or []

        image_url = ""
        for img in images:
            urls = img.get("urls", [])
            if urls:
                val = urls[0].get("value", "")
                if val:
                    image_url = "https:" + val if val.startswith("//") else val
                    break

        price = orig = disc = 0
        pricing = p.get("pricing") or {}
        
        # New Enriched Mapping from RapidAPI schema
        # pricing -> offers -> roomOffers -> pricing -> price -> perRoomPerNight -> exclusive -> display
        offers = pricing.get("offers") or []
        if offers:
            # Iterate through offers and roomOffers to find pricing
            for offer in offers:
                room_offers = offer.get("roomOffers") or []
                if room_offers:
                    ro0 = room_offers[0]
                    # Pricing can be directly in roomOffer or inside its 'room' object
                    pricing_list = ro0.get("pricing") or []
                    if not pricing_list:
                        room_data = ro0.get("room") or {}
                        if isinstance(room_data, dict):
                            pricing_list = room_data.get("pricing") or []
                    
                    if pricing_list:
                        p_info = pricing_list[0].get("price") or {}
                        # We prefer perRoomPerNight for consistent listing
                        pn = p_info.get("perRoomPerNight") or p_info.get("perNight") or p_info.get("perBook") or {}
                        exc = pn.get("exclusive") or pn.get("inclusive") or {}
                        
                        price = exc.get("display", 0)
                        orig = exc.get("crossedOutPrice") or exc.get("originalPrice") or price
                        disc = p_info.get("totalDiscount", 0)
                        if price > 0:
                            break # Found pricing, stop looking in other offers

        score = reviews.get("score", 0)
        rc = reviews.get("reviewCount", 0)
        geo = info.get("geoInfo") or {}
        addr = info.get("address") or {}
        area = addr.get("area") or {}
        acc = info.get("accommodation") or {}
        acc_type = acc.get("accommodationType", 34)

        if acc_type in [34, 33, 35, 111]: pt = "hotel"
        elif acc_type in [29, 120]: pt = "apartment"
        elif acc_type in [28, 131, 37, 122]: pt = "villa"
        else: pt = "hotel"

        # Review quote based on score
        if score >= 9.0:
            quote = "Trên cả tuyệt vời"
        elif score >= 8.0:
            quote = "Tuyệt vời"
        elif score >= 7.0:
            quote = "Rất tốt"
        elif score >= 6.0:
            quote = "Hài lòng"
        else:
            quote = "Điểm đánh giá"

        # Distance description
        highlight = content.get("highlight") or {}
        cc = highlight.get("cityCenter") or {}
        dist_center = cc.get("distanceFromCityCenter")
        if dist_center:
            if dist_center >= 1000:
                dist_desc = f"Cách trung tâm {dist_center / 1000:.1f} km"
            else:
                dist_desc = f"Cách trung tâm {int(dist_center)} m"
        else:
            dist_desc = "Vị trí trung tâm"

        item = {
            "id": str(p.get("propertyId", "")),
            "name": info.get("localeName", info.get("defaultName", "")),
            "propertyType": pt,
            "propertyTypeName": acc.get("accommodationName", "Hotel"),
            "address": area.get("name", ""),
            "city": addr.get("city", {}).get("name", ""),
            "starRating": info.get("rating", info.get("starRating", 0)),
            "score": score,
            "reviewCount": rc,
            "imageUrl": image_url,
            "price": price,
            "originalPrice": orig,
            "discountPercent": disc,
            "latitude": geo.get("latitude", 0),
            "longitude": geo.get("longitude", 0),
            "isPreferred": score >= 8.0,
            "isAvailable": pricing.get("isAvailable", False),
            
            # New fields
            "reviewQuote": quote,
            "distanceDescription": dist_desc,
            
            # snake_case compatibility
            "property_type": pt,
            "property_type_name": acc.get("accommodationName", "Hotel"),
            "star_rating": info.get("rating", info.get("starRating", 0)),
            "review_count": rc,
            "image_url": image_url,
            "original_price": orig,
            "discount_percent": disc,
            "is_preferred": score >= 8.0,
            "is_available": pricing.get("isAvailable", False),
            "review_quote": quote,
            "distance_description": dist_desc
        }
        results.append(item)

    # Prepend local property results to RapidAPI results
    results = local_results + results

    if sort == "Price,Asc":
        results.sort(key=lambda x: (x["price"] == 0, x["price"]))
    elif sort == "Price,Desc":
        results.sort(key=lambda x: x["price"], reverse=True)
    elif sort in ["Ranking,Desc", "Rating,Desc", "Score,Desc", "Review,Desc"]:
        results.sort(key=lambda x: x["score"], reverse=True)

    total_count = len(results)
    city_search_data = data["data"].get("citySearch") if booking_type != "dayuse" else data["data"]
    if city_search_data:
        search_info = city_search_data.get("searchResult", {}).get("searchInfo", {})
        total_count = search_info.get("totalFilteredHotels") or search_info.get("totalActiveHotels") or len(results)

    if include_filters:
        filters = city_search_data.get("aggregation", {}).get("matrixGroupResults", []) if city_search_data else []
        
        if not filters:
            try:
                # Load filters fallback from local filters.json
                filters_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "filters.json")
                if os.path.exists(filters_path):
                    with open(filters_path, "r", encoding="utf-8") as f:
                        fallback_filters_data = json.load(f)
                        filters = []
                        for fg in fallback_filters_data:
                            items_list = []
                            for item in fg.get("items", []):
                                items_list.append({
                                    "id": item.get("id"),
                                    "filterKey": item.get("filterKey"),
                                    "filterRequestType": item.get("filterRequestType"),
                                    "name": item.get("name"),
                                    "count": 15
                                })
                            filters.append({
                                "matrixGroup": fg.get("group"),
                                "matrixItemResults": items_list
                            })
            except Exception as e:
                pass
                
        return {
            "properties": results[:limit],
            "filters": filters,
            "totalCount": total_count
        }

    return results[:limit]

@app.get("/api/properties/{property_id}/details")
def property_details(
    property_id: str,
    checkin: Optional[str] = Query(None),
    checkout: Optional[str] = Query(None),
    fallback_name: Optional[str] = Query(None),
    fallback_city: Optional[str] = Query(None),
    fallback_image: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    if str(property_id).startswith("host_"):
        lp = db.query(models.Property).filter(models.Property.id == property_id).first()
        if not lp:
            raise HTTPException(status_code=404, detail="Local property not found")
        images = lp.image_url.split(",") if lp.image_url else []
        image_urls = [{"url": img.strip(), "caption": "Ảnh chỗ nghỉ", "category": "property"} for img in images]
        if not image_urls:
            image_urls = [{"url": "https://images.unsplash.com/photo-1566073771259-6a8506099945", "caption": "Ảnh chỗ nghỉ", "category": "property"}]
        
        response_data = {
            "id": lp.id,
            "name": lp.name,
            "propertyType": lp.property_type,
            "starRating": lp.star_rating,
            "address": {
                "street": lp.address,
                "area": lp.city,
                "city": lp.city,
                "country": "Việt Nam",
            },
            "latitude": 10.776,
            "longitude": 106.701,
            "description": lp.description or "Chỗ nghỉ sạch sẽ, đầy đủ tiện nghi, vị trí thuận lợi cho du lịch và nghỉ dưỡng.",
            "imageUrls": image_urls,
            "reviewSummary": {"overall": 9.2, "cleanliness": 9.3, "facilities": 9.0, "location": 9.4, "staffPerformance": 9.5, "valueForMoney": 9.1, "reviewCount": 12},
            "travelerGroups": [],
            "reviewSnippets": [
                {"text": "Chỗ nghỉ sạch sẽ, chủ nhà cực kỳ thân thiện và nhiệt tình!", "rating": 10, "reviewer": "Nguyen Lan", "date": "2026-05-15", "country": "Việt Nam"},
                {"text": "Giá cả hợp lý, vị trí gần biển và trung tâm ăn uống.", "rating": 9, "reviewer": "Tran Tuan", "date": "2026-06-01", "country": "Việt Nam"}
            ],
            "favoriteFeatures": [{"id": 1, "name": "Wi-Fi miễn phí", "symbol": "wifi"}, {"id": 2, "name": "Điều hòa", "symbol": "ac"}],
            "nearbyPlaces": [{"name": "Bãi biển", "distance": 0.5, "type": "Beach"}],
            "topPlaces": [],
            "checkIn": "14:00",
            "checkOut": "12:00",
            "featureGroups": [],
            "reviewBreakdown": {"allGuest": {"reviewCount": 12, "grades": {"overall": 9.2}}, "groups": []},
            "nearbyProperties": [],
            "walkablePlaces": {},
            "lastBooked": "Hôm nay",
            "noOfPeopleLooking": 5,
            "additionalPolicies": [],
            "reviewCount": 12,
            "reviewScore": 9.2,
            
            # snake_case compatibility
            "check_in": "14:00",
            "check_out": "12:00",
            "feature_groups": [],
            "review_breakdown": {"allGuest": {"reviewCount": 12, "grades": {"overall": 9.2}}, "groups": []},
            "nearby_properties": [],
            "walkable_places": {},
            "last_booked": "Hôm nay",
            "no_of_people_looking": 5,
            "additional_policies": [],
            "review_count": 12,
            "review_score": 9.2
        }
        return response_data
    pid = property_id.split('_')[-1]
    
    # Calculate default checkin/checkout dates if not provided
    if not checkin:
        checkin = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    if not checkout:
        checkout = (datetime.utcnow() + timedelta(days=2)).strftime("%Y-%m-%d")

    from concurrent.futures import ThreadPoolExecutor

    def fetch_details():
        return rapidapi_get("/hotels/details", {"propertyId": pid, "language": "vi-vn"})

    def fetch_details_others():
        return rapidapi_get("/hotels/details-others", {
            "propertyId": pid,
            "checkinDate": checkin,
            "checkoutDate": checkout,
            "language": "vi-vn",
            "currency": "VND",
            "room": "1",
            "adult": "2"
        })

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_details = executor.submit(fetch_details)
        future_others = executor.submit(fetch_details_others)
        data = future_details.result()
        others_data = future_others.result()

    # Fallback absolute check
    is_error = False
    if not isinstance(data, dict) or not data.get("data"):
        is_error = True
    else:
        details = data["data"].get("propertyDetailsSearch", {}).get("propertyDetails", [])
        if not details:
            is_error = True

    if is_error:
        # absolute database/offline fallback!
        fn = fallback_name or f"Khách sạn Agoda - Mã {pid}"
        fc = fallback_city or "Thành phố Hồ Chí Minh"
        fi = fallback_image or "https://images.unsplash.com/photo-1566073771259-6a8506099945"
        
        fallback_type = "Khách sạn"
        
        db = database.SessionLocal()
        try:
            booking = db.query(models.Booking).filter(models.Booking.property_id == property_id).first()
            if booking:
                fallback_name = booking.property_name
                fallback_type = booking.property_type or "Hotel"
                fallback_image = booking.property_image
        except:
            pass
        finally:
            db.close()
            
        fallback_images = [
            {"url": fi, "caption": "Ảnh tổng quan", "category": "property"},
            {"url": "https://images.unsplash.com/photo-1582719508461-905c673771fd", "caption": "Phòng nghỉ ấm cúng", "category": "room"},
            {"url": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4", "caption": "Hồ bơi thư giãn", "category": "facility"}
        ]
        
        fallback_res = {
            "id": property_id,
            "name": fn,
            "propertyType": fallback_type,
            "starRating": 4,
            "address": {
                "street": "Trung tâm",
                "area": fc,
                "city": fc,
                "country": "Việt Nam",
            },
            "latitude": 10.776,
            "longitude": 106.701,
            "description": "Khách sạn nghỉ dưỡng sang trọng, vị trí trung tâm thuận tiện di chuyển. Đầy đủ tiện nghi hiện đại và dịch vụ đẳng cấp.",
            "imageUrls": fallback_images,
            "reviewSummary": {"overall": 8.0, "cleanliness": 8.0, "facilities": 8.0, "location": 8.0, "staffPerformance": 8.0, "valueForMoney": 8.0, "reviewCount": 10},
            "travelerGroups": [],
            "reviewSnippets": [],
            "favoriteFeatures": [],
            "nearbyPlaces": [],
            "topPlaces": [],
            "checkIn": "14:00",
            "checkOut": "12:00",
            "featureGroups": [],
            "reviewBreakdown": {"allGuest": {"reviewCount": 10, "grades": {"overall": 8.0}}, "groups": []},
            "nearbyProperties": [],
            "walkablePlaces": {},
            "lastBooked": "",
            "noOfPeopleLooking": 2,
            "additionalPolicies": [],
            "reviewCount": 10,
            "reviewScore": 8.0,
            
            # snake_case compatibility
            "check_in": "14:00",
            "check_out": "12:00",
            "feature_groups": [],
            "review_breakdown": {"allGuest": {"reviewCount": 10, "grades": {"overall": 8.0}}, "groups": []},
            "nearby_properties": [],
            "walkable_places": {},
            "last_booked": "",
            "no_of_people_looking": 2,
            "additional_policies": [],
            "review_count": 10,
            "review_score": 8.0
        }
        return fallback_res

    detail = details[0]
    content = detail.get("contentDetail", {})
    summary = content.get("contentSummary", {})
    review_score = content.get("contentReviewScore", {})
    highlights = content.get("contentHighlights", {})
    information = content.get("contentInformation", {})
    images_data = content.get("contentImages", {})
    local_info = content.get("contentLocalInformation", {})

    image_urls = []
    for img in images_data.get("hotelImages", []):
        for url in img.get("urls", []):
            val = url.get("value", "")
            if val:
                image_urls.append({
                    "url": "https:" + val if val.startswith("//") else val,
                    "caption": img.get("caption", ""),
                    "category": img.get("groupId", "other")
                })

    review_summary = {}
    traveler_groups = []
    providers = review_score.get("providerReviewScore", [])
    if providers:
        dp = next((p for p in providers if p.get("isDefault")), providers[0])
        ag = dp.get("demographics", {}).get("allGuest", {})
        for g in ag.get("grades", []):
            review_summary[g.get("id", "")] = g.get("score", 0)
        review_summary["reviewCount"] = ag.get("reviewCount", 0)
        traveler_groups = dp.get("demographics", {}).get("groups", [])

    favorite_features = [{"id": f.get("id"), "name": f.get("name", ""), "symbol": f.get("symbol", "")} for f in highlights.get("favoriteFeatures", [])]

    review_snippets = []
    for s in content.get("contentReviewSummaries", {}).get("snippets", []):
        review_snippets.append({
            "text": s.get("snippet", ""),
            "rating": s.get("reviewRating", 0),
            "reviewer": s.get("reviewer", ""),
            "date": s.get("date", ""),
            "country": s.get("countryName", "")
        })

    geo = summary.get("geoInfo", {})
    addr = summary.get("address", {})
    acc = summary.get("accommodation", {})
    desc = information.get("description", {})

    # Groups and breakdown for demographics
    review_breakdown = {
        "allGuest": {
            "reviewCount": 0,
            "grades": {}
        },
        "groups": []
    }
    
    if providers:
        dp = next((p for p in providers if p.get("isDefault")), providers[0])
        ag = dp.get("demographics", {}).get("allGuest", {})
        
        # Populate allGuest
        review_breakdown["allGuest"]["reviewCount"] = ag.get("reviewCount", 0)
        for g in ag.get("grades", []):
            review_breakdown["allGuest"]["grades"][g.get("id", "")] = g.get("score", 0)
            
        # Populate groups
        TRAVELER_GROUP_NAMES = {
            1: "Khách công tác",
            2: "Cặp đôi",
            3: "Du lịch cá nhân",
            4: "Gia đình có trẻ nhỏ",
            5: "Gia đình có thanh thiếu niên",
            6: "Nhóm bạn"
        }
        demographics = dp.get("demographics") or {}
        for grp in demographics.get("groups") or []:
            grp_id = grp.get("id", 0)
            grades_dict = {}
            for g in grp.get("grades") or []:
                grades_dict[g.get("id", "")] = g.get("score", 0)
            review_breakdown["groups"].append({
                "id": grp_id,
                "name": TRAVELER_GROUP_NAMES.get(grp_id, f"Nhóm {grp_id}"),
                "reviewCount": grp.get("reviewCount", 0),
                "grades": grades_dict
            })

    # Feature Groups mapping
    feature_groups = []
    cf = content.get("contentFeatures") or {}
    for fg in cf.get("featureGroups") or []:
        features_list = []
        for feat in fg.get("features") or []:
            feat_images = []
            for img in feat.get("images") or []:
                for u in img.get("urls") or []:
                    val = u.get("value", "")
                    if val:
                        feat_images.append({
                            "url": "https:" + val if val.startswith("//") else val,
                            "caption": img.get("caption", "")
                        })
            features_list.append({
                "id": feat.get("id"),
                "name": feat.get("featureName", ""),
                "symbol": feat.get("symbol", ""),
                "available": feat.get("available", True),
                "order": feat.get("order", 0),
                "images": feat_images
            })
        feature_groups.append({
            "id": fg.get("id"),
            "name": fg.get("name", ""),
            "order": fg.get("order", 0),
            "features": features_list
        })

    # Categorized nearby properties
    nearby_properties = []
    for category in local_info.get("nearbyProperties") or []:
        places = []
        for p in category.get("places") or []:
            places.append({
                "name": p.get("name", ""),
                "distanceInKm": p.get("distanceInKm", 0)
            })
        nearby_properties.append({
            "categoryName": category.get("categoryName", ""),
            "categorySymbol": category.get("categorySymbol", ""),
            "places": places
        })

    # Walkable places
    walkable_places = {}
    wp_data = local_info.get("walkablePlaces", {})
    if wp_data:
        walkable_places = {
            "title": wp_data.get("title", ""),
            "description": wp_data.get("description", ""),
            "totalCount": wp_data.get("totalCount", 0)
        }

    # Content Engagement
    engagement = content.get("contentEngagement", {})
    last_booked = engagement.get("lastBooked", "")
    no_of_people_looking = engagement.get("noOfPeopleLooking", 0)

    # Check-in/out default values from details
    content_info = content.get("contentInformation", {})
    check_in_info_details = content_info.get("checkInInformation", {})
    
    def parse_time(t_obj, default_time):
        if not t_obj: return default_time
        if isinstance(t_obj, str): return t_obj
        if isinstance(t_obj, dict):
            hh = t_obj.get("hh", 0)
            mm = t_obj.get("mm", 0)
            return f"{hh:02d}:{mm:02d}"
        return default_time

    check_in_time = parse_time(check_in_info_details.get("checkInFrom"), "14:00")
    check_out_time = parse_time(check_in_info_details.get("checkOutUntil"), "12:00")
    additional_policies = []

    # Helper function to find property_context in details-others response
    def find_property_context(obj):
        if isinstance(obj, dict):
            if obj.get("type") == "property_context":
                return obj
            for v in obj.values():
                res = find_property_context(v)
                if res:
                    return res
        elif isinstance(obj, list):
            for item in obj:
                res = find_property_context(item)
                if res:
                    return res
        return None

    # Parse details-others details if available
    prop_context = find_property_context(others_data)
    if prop_context:
        summary_others = prop_context.get("summary", {})
        check_in_info_others = summary_others.get("checkInInformation", {})
        if check_in_info_others.get("checkInFrom"):
            check_in_time = check_in_info_others.get("checkInFrom")
        if check_in_info_others.get("checkOutUntil"):
            check_out_time = check_in_info_others.get("checkOutUntil")
            
        policy_others = prop_context.get("policy", {})
        if "additionalPolicies" in policy_others:
            additional_policies = policy_others.get("additionalPolicies", [])

    # Review cumulative scores
    combined_review = review_score.get("combinedReviewScore", {})
    cumulative_review = combined_review.get("cumulative", {})
    review_score_val = cumulative_review.get("score", summary.get("rating", 0.0))
    review_count_val = cumulative_review.get("reviewCount", 0)

    # Format the translated address
    address_street = clean_street_address(
        addr.get("address1", ""),
        addr.get("area", {}).get("name", ""),
        addr.get("city", {}).get("name", ""),
        addr.get("country", {}).get("name", "")
    )
    address_street = translate_address_to_vietnamese(address_street)

    response_data = {
        "id": property_id,
        "name": summary.get("localeName", summary.get("defaultName", "")),
        "propertyType": acc.get("accommodationName", "Hotel"),
        "starRating": summary.get("rating", 0),
        "address": {
            "street": address_street,
            "area": addr.get("area", {}).get("name", ""),
            "city": addr.get("city", {}).get("name", ""),
            "country": addr.get("country", {}).get("name", ""),
        },
        "latitude": geo.get("latitude", 0),
        "longitude": geo.get("longitude", 0),
        "description": desc.get("long", desc.get("short", "")),
        "imageUrls": image_urls,
        "reviewSummary": review_summary,
        "travelerGroups": traveler_groups,
        "reviewSnippets": review_snippets,
        "favoriteFeatures": favorite_features,
        "nearbyPlaces": [{"name": np.get("name", ""), "distance": np.get("distanceInKm", 0), "type": np.get("typeName", "")} for np in local_info.get("nearbyPlaces", [])[:5]],
        "topPlaces": [{"name": tp.get("name", ""), "distance": tp.get("distanceInKm", 0), "type": tp.get("typeName", "")} for tp in local_info.get("topPlaces", [])[:5]],
        
        # New enriched fields
        "checkIn": check_in_time,
        "checkOut": check_out_time,
        "featureGroups": feature_groups,
        "reviewBreakdown": review_breakdown,
        "nearbyProperties": nearby_properties,
        "walkablePlaces": walkable_places,
        "lastBooked": last_booked,
        "noOfPeopleLooking": no_of_people_looking,
        "additionalPolicies": additional_policies,
        "reviewCount": review_count_val,
        "reviewScore": review_score_val
    }

    # Add snake_case keys for Android compatibility
    android_keys = {
        "check_in": check_in_time,
        "check_out": check_out_time,
        "feature_groups": feature_groups,
        "review_breakdown": review_breakdown,
        "nearby_properties": nearby_properties,
        "walkable_places": walkable_places,
        "last_booked": last_booked,
        "no_of_people_looking": no_of_people_looking,
        "additional_policies": additional_policies,
        "review_count": review_count_val,
        "review_score": review_score_val
    }
    response_data.update(android_keys)

    return response_data

@app.get("/api/properties/{property_id}/rooms")
def get_property_rooms(
    property_id: str,
    checkin: str = Query(...),
    checkout: str = Query(...),
    room: int = 1,
    adult: int = 2,
    childAges: Optional[str] = None,
    db: Session = Depends(get_db)
):
    if str(property_id).startswith("host_"):
        lp = db.query(models.Property).filter(models.Property.id == property_id).first()
        if not lp:
            raise HTTPException(status_code=404, detail="Local property not found")
        images = lp.image_url.split(",") if lp.image_url else ["https://images.unsplash.com/photo-1590490360182-c33d57733427"]
        img_standard = images[0].strip()
        img_deluxe = images[1].strip() if len(images) > 1 else images[0].strip()
        return [
            {
                "id": f"{lp.id}_std",
                "roomName": "Phòng Tiêu Chuẩn (Standard Room)",
                "room_name": "Phòng Tiêu Chuẩn (Standard Room)",
                "amenities": "Wi-Fi miễn phí, Điều hòa, Phòng tắm riêng, Tivi LCD, Diện tích: 25 m²",
                "price": lp.price,
                "originalPrice": lp.price * 1.2,
                "original_price": lp.price * 1.2,
                "isAvailable": True,
                "is_available": True,
                "occupancy": {"maxAdults": 2, "maxChildren": 1},
                "imageUrl": img_standard,
                "image_url": img_standard,
                "images": [img_standard],
                "breakfastIncluded": False,
                "breakfast_included": False,
                "cancellationPolicy": "Hủy miễn phí trước 24 giờ nhận phòng",
                "cancellation_policy": "Hủy miễn phí trước 24 giờ nhận phòng",
                "cancellationPolicyType": 1,
                "cancellation_policy_type": 1,
                "isFreeCancellation": True,
                "is_free_cancellation": True,
                "remainRoom": 3,
                "remain_room": 3,
                "roomOccupancyDescription": "Tối đa 2 người lớn",
                "room_occupancy_description": "Tối đa 2 người lớn",
                "benefits": [{"id": 10001, "displayText": "Hủy miễn phí trước 24 giờ", "available": True}],
                "checkIn": "14:00",
                "checkOut": "12:00",
                "check_in": "14:00",
                "check_out": "12:00"
            },
            {
                "id": f"{lp.id}_dlx",
                "roomName": "Phòng Deluxe Cao Cấp (Deluxe Room)",
                "room_name": "Phòng Deluxe Cao Cấp (Deluxe Room)",
                "amenities": "Bao gồm ăn sáng, Wi-Fi miễn phí, Điều hòa, Ban công hướng phố, Diện tích: 35 m²",
                "price": lp.price * 1.3,
                "originalPrice": lp.price * 1.5,
                "original_price": lp.price * 1.5,
                "isAvailable": True,
                "is_available": True,
                "occupancy": {"maxAdults": 2, "maxChildren": 2},
                "imageUrl": img_deluxe,
                "image_url": img_deluxe,
                "images": [img_deluxe],
                "breakfastIncluded": True,
                "breakfast_included": True,
                "cancellationPolicy": "Hủy miễn phí trước 24 giờ nhận phòng",
                "cancellation_policy": "Hủy miễn phí trước 24 giờ nhận phòng",
                "cancellationPolicyType": 1,
                "cancellation_policy_type": 1,
                "isFreeCancellation": True,
                "is_free_cancellation": True,
                "remainRoom": 2,
                "remain_room": 2,
                "roomOccupancyDescription": "Tối đa 2 người lớn, 2 trẻ em",
                "room_occupancy_description": "Tối đa 2 người lớn, 2 trẻ em",
                "benefits": [{"id": 10002, "displayText": "Bao gồm ăn sáng", "available": True}, {"id": 10001, "displayText": "Hủy miễn phí trước 24 giờ", "available": True}],
                "checkIn": "14:00",
                "checkOut": "12:00",
                "check_in": "14:00",
                "check_out": "12:00"
            }
        ]
    pid = property_id.split('_')[-1]
    params = {
        "propertyId": pid,
        "checkinDate": checkin,
        "checkoutDate": checkout,
        "language": "vi-vn",
        "room": str(room),
        "adult": str(adult)
    }
    if childAges:
        params["childAges"] = childAges

    # Lấy danh sách ảnh phòng từ details khách sạn trước (dùng cache nếu có)
    room_images = []
    check_in_time = "14:00"
    check_out_time = "12:00"
    try:
        details_data = rapidapi_get("/hotels/details", {"propertyId": pid, "language": "vi-vn"})
        if details_data and details_data.get("data"):
            details = details_data["data"].get("propertyDetailsSearch", {}).get("propertyDetails", [])
            if details:
                content = details[0].get("contentDetail", {})
                images_data = content.get("contentImages", {})
                for img in images_data.get("hotelImages", []):
                    if img.get("groupId") == "room":
                        for url in img.get("urls", []):
                            val = url.get("value", "")
                            if val:
                                room_images.append("https:" + val if val.startswith("//") else val)
                                break
                
                # Fallback: nếu khách sạn không có nhóm 'room', lấy tất cả các ảnh hiện có
                if not room_images:
                    for img in images_data.get("hotelImages", []):
                        for url in img.get("urls", []):
                            val = url.get("value", "")
                            if val:
                                room_images.append("https:" + val if val.startswith("//") else val)
                                break
                content_info = content.get("contentInformation", {})
                check_in_info_details = content_info.get("checkInInformation", {})
                if check_in_info_details.get("checkInFrom"):
                    check_in_time = check_in_info_details.get("checkInFrom")
                if check_in_info_details.get("checkOutUntil"):
                    check_out_time = check_in_info_details.get("checkOutUntil")
    except Exception:
        pass

    data = rapidapi_get("/hotels/room-grid", params)
    
    # Nếu room-grid không trả về data, thử fallback sang room-prices
    if not data or not data.get("roomGroups"):
        data = rapidapi_get("/hotels/room-prices", params)

    # Thử lấy checkin/checkout từ room-grid/prices property_context
    def find_property_context(obj):
        if isinstance(obj, dict):
            if obj.get("type") == "property_context":
                return obj
            for v in obj.values():
                res = find_property_context(v)
                if res:
                    return res
        elif isinstance(obj, list):
            for item in obj:
                res = find_property_context(item)
                if res:
                    return res
        return None

    prop_context = find_property_context(data)
    if prop_context:
        summary_others = prop_context.get("summary", {})
        check_in_info_others = summary_others.get("checkInInformation", {})
        if check_in_info_others.get("checkInFrom"):
            check_in_time = check_in_info_others.get("checkInFrom")
        if check_in_info_others.get("checkOutUntil"):
            check_out_time = check_in_info_others.get("checkOutUntil")

    rooms = []
    if data and data.get("roomGroups"):
        for g_idx, g in enumerate(data.get("roomGroups", [])):
            room_name = g.get("masterRoomTypeName") or g.get("masterRoomTypeEnglishName") or "Room"
            
            # Thử lấy hướng phòng, diện tích phòng từ room đầu tiên trong group
            group_rooms = g.get("rooms", [])
            group_room_view = ""
            group_room_size = 0.0
            if group_rooms:
                group_room_view = group_rooms[0].get("roomView", "")
                group_room_size = group_rooms[0].get("roomSize", 0.0)
                
            for r in group_rooms:
                pricing = r.get("pricingDisplaySummary", {})
                per_night = pricing.get("perRoomPerNight", {})
                charge = per_night.get("chargeTotal", {})
                price = charge.get("exclusive", 0.0) or charge.get("allInclusive", 0.0)
                original = per_night.get("originalTotal", {}).get("exclusive", 0.0) or per_night.get("originalTotal", {}).get("allInclusive", 0.0) or price
                
                benefits_list = r.get("benefits", [])
                
                # Tối ưu danh sách tiện ích phòng
                amenities_parts = []
                if group_room_view:
                    amenities_parts.append(f"Hướng: {group_room_view}")
                if group_room_size and float(group_room_size) > 0:
                    amenities_parts.append(f"Diện tích: {group_room_size} m²")
                
                group_bed_type = g.get("bedType", "")
                if group_bed_type:
                    amenities_parts.append(f"Giường: {group_bed_type}")
                
                for b in benefits_list:
                    txt = b.get("displayText", "")
                    if txt and txt not in amenities_parts:
                        amenities_parts.append(txt)
                        
                # Thêm một vài tiện ích cơ bản nếu danh sách quá ngắn
                if len(amenities_parts) < 3:
                    default_facilities = ["Điều hòa nhiệt độ", "Wi-Fi miễn phí", "Tivi LCD", "Đồ vệ sinh cá nhân miễn phí", "Két an toàn"]
                    for df in default_facilities:
                        if df not in amenities_parts and len(amenities_parts) < 4:
                            amenities_parts.append(df)
                            
                amenities = ", ".join(amenities_parts)
                
                # Lấy danh sách ảnh cho riêng nhóm phòng này
                group_images = g.get("images", [])
                room_image_list = []
                for img_obj in group_images:
                    # In /hotels/room-prices, it's 'url' directly. In /hotels/details it's 'urls' array.
                    val = img_obj.get("url", "")
                    if not val:
                        urls = img_obj.get("urls", [])
                        if urls:
                            val = urls[0].get("value", "")
                    
                    if val:
                        room_image_list.append("https:" + val if val.startswith("//") else val)

                if not room_image_list:
                    if room_images:
                        # Gán tất cả ảnh hiện có cho phòng thay vì giới hạn 3 ảnh
                        room_image_list.extend(room_images)
                    else:
                        # Multiple fallback images if property has no images
                        fallbacks = [
                            "https://images.unsplash.com/photo-1590490360182-c33d57733427",
                            "https://images.unsplash.com/photo-1566665797739-1674de7a421a",
                            "https://images.unsplash.com/photo-1631049307264-da0ec9d70304",
                            "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b",
                            "https://images.unsplash.com/photo-1611892440504-42a792e24d32"
                        ]
                        start_idx = (g_idx * 3) % len(fallbacks)
                        for i in range(len(fallbacks)):
                            idx = (start_idx + i) % len(fallbacks)
                            if fallbacks[idx] not in room_image_list:
                                room_image_list.append(fallbacks[idx])

                img_url = room_image_list[0]
                
                rooms.append({
                    "id": r.get("uid", "")[:20] or r.get("roomToken", "")[:20],
                    "roomName": room_name,
                    "room_name": room_name,
                    "amenities": amenities,
                    "price": price,
                    "originalPrice": original,
                    "original_price": original,
                    "isAvailable": True,
                    "is_available": True,
                    "occupancy": r.get("occupancy", {}),
                    "imageUrl": img_url,
                    "image_url": img_url,
                    "images": room_image_list,
                    
                    # New fields
                    "breakfastIncluded": r.get("breakfastIncluded", False),
                    "breakfast_included": r.get("breakfastIncluded", False),
                    "cancellationPolicy": r.get("cancellationPolicy", ""),
                    "cancellation_policy": r.get("cancellationPolicy", ""),
                    "cancellationPolicyType": r.get("cancellationPolicyType", 0),
                    "cancellation_policy_type": r.get("cancellationPolicyType", 0),
                    "isFreeCancellation": r.get("cancellationPolicyType", 0) != 0,
                    "is_free_cancellation": r.get("cancellationPolicyType", 0) != 0,
                    "remainRoom": r.get("remainRoom", 5),
                    "remain_room": r.get("remainRoom", 5),
                    "roomOccupancyDescription": r.get("roomOccupancyDescription", ""),
                    "room_occupancy_description": r.get("roomOccupancyDescription", ""),
                    "benefits": [{"id": b.get("id"), "displayText": b.get("displayText", ""), "available": b.get("available", True)} for b in benefits_list],
                    "checkIn": check_in_time,
                    "checkOut": check_out_time,
                    "check_in": check_in_time,
                    "check_out": check_out_time
                })

    # Fallback to search if both failed
    if not rooms:
        search_params = {"id": f"1_{pid}", "checkinDate": checkin, "checkoutDate": checkout, "limit": "1", "room": str(room), "adult": str(adult)}
        if childAges: search_params["childAges"] = childAges
        search_data = rapidapi_get("/hotels/search-overnight", search_params)
        if search_data.get("data"):
            props = search_data["data"].get("citySearch", {}).get("properties", [])
            if props:
                for offer_idx, offer in enumerate(props[0].get("pricing", {}).get("offers", [])):
                    for ro_idx, ro in enumerate(offer.get("roomOffers", [])):
                        room_obj = ro.get("room", {})
                        pl = ro.get("pricing", [])
                        if not pl and isinstance(room_obj, dict):
                            pl = room_obj.get("pricing", [])
                        price = orig = 0
                        if pl:
                            pn = pl[0].get("price", {}).get("perRoomPerNight", {}).get("exclusive", {})
                            price = pn.get("display", 0)
                            orig = pn.get("crossedOutPrice", 0)
                            
                        room_name = f"Phòng tiêu chuẩn (cho {room_obj.get('occupancy', 2) if isinstance(room_obj, dict) else 2} khách)"
                        
                        # Fallback amenities
                        amenities_parts = []
                        if isinstance(room_obj, dict):
                            for b in room_obj.get("benefits", []):
                                d = b.get("description", "")
                                if d: amenities_parts.append(d)
                        if len(amenities_parts) < 3:
                            amenities_parts.extend(["Wi-Fi miễn phí", "Điều hòa nhiệt độ", "Tivi LCD", "Đồ vệ sinh cá nhân miễn phí"])
                        amenities = ", ".join(amenities_parts[:4])
                        
                        img_url = ""
                        if room_images:
                            img_url = room_images[offer_idx % len(room_images)]
                        else:
                            img_url = "https://images.unsplash.com/photo-1590490360182-c33d57733427"
                            
                        rooms.append({
                            "id": room_obj.get("uid", "")[:20] if isinstance(room_obj, dict) else "",
                            "roomName": room_name,
                            "room_name": room_name,
                            "amenities": amenities,
                            "price": price,
                            "originalPrice": orig,
                            "original_price": orig,
                            "isAvailable": True,
                            "is_available": True,
                            "imageUrl": img_url,
                            "image_url": img_url,
                            "breakfastIncluded": True,
                            "breakfast_included": True,
                            "cancellationPolicy": "Hủy miễn phí trước 24 giờ nhận phòng",
                            "cancellation_policy": "Hủy miễn phí trước 24 giờ nhận phòng",
                            "cancellationPolicyType": 1,
                            "cancellation_policy_type": 1,
                            "isFreeCancellation": True,
                            "is_free_cancellation": True,
                            "remainRoom": 5,
                            "remain_room": 5,
                            "roomOccupancyDescription": "Tối đa 2 khách",
                            "room_occupancy_description": "Tối đa 2 khách",
                            "benefits": [{"id": 10002, "displayText": "Bao gồm ăn sáng", "available": True}],
                            "checkIn": check_in_time,
                            "checkOut": check_out_time,
                            "check_in": check_in_time,
                            "check_out": check_out_time
                        })

    # If still no rooms, absolute offline fallback
    if not rooms:
        fallback_types = [
            {"name": "Phòng Deluxe (Deluxe Room)", "price": 1200000.0, "original": 1500000.0, "breakfast": True, "cancel_type": 1, "cancel_policy": "Hủy miễn phí trước 24 giờ trước khi nhận phòng"},
            {"name": "Phòng Superior (Superior Room)", "price": 950000.0, "original": 1100000.0, "breakfast": True, "cancel_type": 0, "cancel_policy": "Không hoàn tiền"},
            {"name": "Phòng Suite Sang Trọng (Suite Room)", "price": 2100000.0, "original": 2500000.0, "breakfast": True, "cancel_type": 1, "cancel_policy": "Hủy miễn phí trước 48 giờ trước khi nhận phòng"}
        ]
        for idx, fbr in enumerate(fallback_types):
            img_url = room_images[idx % len(room_images)] if room_images else "https://images.unsplash.com/photo-1590490360182-c33d57733427"
            rooms.append({
                "id": f"fb_room_{idx}_{pid}",
                "roomName": fbr["name"],
                "room_name": fbr["name"],
                "amenities": "Hướng: Thành phố, Diện tích: 32 m², Điều hòa nhiệt độ, Wi-Fi miễn phí, Tivi LCD, Đồ vệ sinh cá nhân miễn phí",
                "price": fbr["price"],
                "originalPrice": fbr["original"],
                "original_price": fbr["original"],
                "isAvailable": True,
                "is_available": True,
                "occupancy": {"maxAdults": 2, "maxChildren": 1},
                "imageUrl": img_url,
                "image_url": img_url,
                "breakfastIncluded": fbr["breakfast"],
                "breakfast_included": fbr["breakfast"],
                "cancellationPolicy": fbr["cancel_policy"],
                "cancellation_policy": fbr["cancel_policy"],
                "cancellationPolicyType": fbr["cancel_type"],
                "cancellation_policy_type": fbr["cancel_type"],
                "isFreeCancellation": fbr["cancel_type"] != 0,
                "is_free_cancellation": fbr["cancel_type"] != 0,
                "remainRoom": 3,
                "remain_room": 3,
                "roomOccupancyDescription": "Tối đa 2 người lớn, 1 trẻ em",
                "room_occupancy_description": "Tối đa 2 người lớn, 1 trẻ em",
                "benefits": [{"id": 10002, "displayText": "Bao gồm ăn sáng", "available": True}],
                "checkIn": check_in_time,
                "checkOut": check_out_time,
                "check_in": check_in_time,
                "check_out": check_out_time
            })

    return rooms

@app.get("/api/properties/{property_id}/reviews")
def get_property_reviews(
    property_id: str,
    page: int = 1,
    limit: int = 20,
    sort: int = 7, # 7: Most helpful
    travelerType: int = 0,
    reviewSources: str = "-1"
):
    pid = property_id.split('_')[-1]
    params = {
        "propertyId": pid,
        "page": str(page),
        "limit": str(limit),
        "sort": str(sort),
        "travelerType": str(travelerType),
        "reviewSources": reviewSources,
        "language": "vi-vn"
    }
    
    data = rapidapi_get("/hotels/reviews", params)
    
    if data and "comments" in data:
        return data
        
    return {"comments": []}

# ==============================================================================
# AUTH
# ==============================================================================
@app.post("/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    from sqlalchemy.exc import IntegrityError
    # Validate email format
    if not validate_email(user.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    # Validate password length
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    # Validate full_name
    if not user.full_name or not user.full_name.strip():
        raise HTTPException(status_code=400, detail="Full name is required")
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed = hash_password(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed, full_name=user.full_name.strip())
    try:
        db.add(new_user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")
    return {"message": "Registration successful"}

@app.post("/auth/login")
def login(data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Login nhận Body JSON thay vì Query params để bảo mật password."""
    hashed = hash_password(data.password)
    user = db.query(models.User).filter(
        models.User.email == data.email,
        models.User.hashed_password == hashed
    ).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    response.set_cookie(key="user_id", value=str(user.id), httponly=True, max_age=86400*30, path="/")
    return {"message": "Login successful", "user_id": user.id, "full_name": user.full_name, "email": user.email}

@app.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie("user_id", path="/")
    return {"message": "Logout successful"}

@app.put("/auth/profile/{user_id}")
def update_profile(user_id: int, data: ProfileUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not data.full_name.strip():
        raise HTTPException(status_code=400, detail="Full name cannot be empty")
    user.full_name = data.full_name.strip()
    db.commit()
    # Trả về format nhất quán với login response để Android dùng được
    return {"message": "Updated", "user_id": user.id, "full_name": user.full_name, "email": user.email}

def calculate_vip_status(bookings_count: int, total_spent: float):
    if bookings_count >= 15 and total_spent >= 37500000:
        return "VIP Diamond"
    if bookings_count >= 10 or total_spent >= 10000000:
        return "VIP Platinum"
    if bookings_count >= 5 or total_spent >= 5000000:
        return "VIP Gold"
    if bookings_count >= 2:
        return "VIP Silver"
    return "VIP Bronze"

# Extended User Endpoints (AgodaCash, VIP, Inbox, Reviews)
# ==============================================================================
class ReviewCreate(BaseModel):
    booking_id: int
    property_name: str
    rating: float
    comment: str

@app.get("/api/user/agodacash")
def get_user_agodacash(user=Depends(get_current_user_from_cookie), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {
        "balance": user.agodacash_balance,
        "transactions": [
            {"date": "2026-06-01", "description": "Hoàn tiền phòng VIP", "amount": 50000},
            {"date": "2026-06-10", "description": "Tặng điểm thành viên mới", "amount": 100000}
        ] if user.agodacash_balance > 0 else []
    }

@app.get("/api/user/vip")
def get_user_vip(user=Depends(get_current_user_from_cookie), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {
        "tier": user.vip_tier,
        "points": user.vip_points,
        "progress": user.vip_progress,
        "next_tier": "Silver" if user.vip_tier == "Bronze" else ("Gold" if user.vip_tier == "Silver" else "Platinum")
    }

@app.get("/api/inbox")
def get_user_inbox(user=Depends(get_current_user_from_cookie), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    messages = db.query(models.InboxMessage).filter(models.InboxMessage.user_id == user.id).order_by(models.InboxMessage.created_at.desc()).all()
    if not messages:
        # Tự động tạo 1 tin nhắn mẫu nếu chưa có
        msg = models.InboxMessage(user_id=user.id, sender_name="Agoda Support", subject="Chào mừng bạn!", content="Chào mừng bạn đến với Agoda Clone. Chúc bạn có những chuyến đi tuyệt vời!", is_read=False)
        db.add(msg)
        db.commit()
        db.refresh(msg)
        messages = [msg]
        
    return [{"id": m.id, "sender": m.sender_name, "subject": m.subject, "content": m.content, "is_read": m.is_read, "date": m.created_at.strftime("%Y-%m-%d %H:%M")} for m in messages]

@app.post("/api/inbox/mark_read/{msg_id}")
def mark_inbox_read(msg_id: int, user=Depends(get_current_user_from_cookie), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    msg = db.query(models.InboxMessage).filter(models.InboxMessage.id == msg_id, models.InboxMessage.user_id == user.id).first()
    if msg:
        msg.is_read = True
        db.commit()
    return {"status": "success"}

@app.get("/api/reviews")
def get_user_reviews(user=Depends(get_current_user_from_cookie), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    reviews = db.query(models.Review).filter(models.Review.user_id == user.id).order_by(models.Review.created_at.desc()).all()
    return [{"id": r.id, "booking_id": r.booking_id, "property_name": r.property_name, "rating": r.rating, "comment": r.comment, "date": r.created_at.strftime("%Y-%m-%d")} for r in reviews]

@app.post("/api/reviews")
def create_review(review: ReviewCreate, user=Depends(get_current_user_from_cookie), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    new_rev = models.Review(
        user_id=user.id,
        booking_id=review.booking_id,
        property_name=review.property_name,
        rating=review.rating,
        comment=review.comment
    )
    db.add(new_rev)
    
    # Tặng 10000 VNĐ AgodaCash khi viết đánh giá
    user.agodacash_balance += 10000
    
    db.commit()
    return {"status": "success", "reward": 10000}
@app.get("/api/user/{user_id}")
def get_user_info(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    bookings = db.query(models.Booking).filter(models.Booking.user_id == user_id).all()
    
    # Calculate completed bookings and total spent
    # Currently status might be "confirmed", we treat all non-cancelled as contributing to VIP
    valid_bookings = [b for b in bookings if b.status != "cancelled"]
    bookings_count = len(valid_bookings)
    total_spent = sum(b.total_price for b in valid_bookings)
    
    vip_status = calculate_vip_status(bookings_count, total_spent)
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "vip_points": user.vip_points,
        "vip_status": vip_status,
        "bookings_count": bookings_count,
        "total_spent": total_spent
    }

# ==============================================================================
# BOOKINGS
# ==============================================================================
@app.post("/bookings")
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    # Verify user tồn tại
    user = db.query(models.User).filter(models.User.id == booking.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate date format
    if not validate_date_format(booking.checkin_date) or not validate_date_format(booking.checkout_date):
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Validate checkin < checkout
    checkin = datetime.strptime(booking.checkin_date, '%Y-%m-%d')
    checkout = datetime.strptime(booking.checkout_date, '%Y-%m-%d')
    if checkin >= checkout:
        raise HTTPException(status_code=400, detail="Checkout date must be after checkin date")

    # Validate original_price > 0
    if booking.original_price <= 0:
        raise HTTPException(status_code=400, detail="Invalid price")

    # Tính discount chỉ từ server — không tin discount từ client
    discount = 0.0
    promo_id = None

    if booking.promotion_code:
        promo = db.query(models.Promotion).filter(
            models.Promotion.code == booking.promotion_code.upper(),
            models.Promotion.is_active == True
        ).first()
        if promo:
            now = datetime.utcnow()
            if promo.valid_from and promo.valid_from > now:
                raise HTTPException(status_code=400, detail="Promo not yet active")
            if promo.valid_until and promo.valid_until < now:
                raise HTTPException(status_code=400, detail="Promo expired")
            if promo.current_usage >= promo.max_usage:
                raise HTTPException(status_code=400, detail="Promo maxed out")
            discount = booking.original_price * (promo.discount_percent / 100)
            promo_id = promo.id
            # Tăng usage TRONG CÙNG transaction để đảm bảo atomic
            promo.current_usage += 1

    final_price = max(booking.original_price - discount, 0)

    new_booking = models.Booking(
        user_id=booking.user_id,
        promotion_id=promo_id,
        property_id=booking.property_id,
        property_name=booking.property_name,
        property_type=booking.property_type,
        property_image=booking.property_image,
        checkin_date=booking.checkin_date,
        checkin_time=booking.checkin_time,
        checkout_date=booking.checkout_date,
        total_price=final_price,
        original_price=booking.original_price,
        discount_amount=discount
    )
    db.add(new_booking)
    db.commit()  # Commit cả promo usage và booking cùng lúc
    return {"status": "success", "message": "Booking successful!", "booking_id": new_booking.id}

@app.get("/bookings/{user_id}")
def get_user_bookings(user_id: int, db: Session = Depends(get_db)):
    bookings = db.query(models.Booking).filter(models.Booking.user_id == user_id).order_by(models.Booking.id.desc()).all()
    return [{
        "id": b.id,
        "property_id": b.property_id,
        "property_name": b.property_name,
        "property_type": b.property_type,
        "property_image": b.property_image,
        "checkin_date": b.checkin_date,
        "checkout_date": b.checkout_date,
        "total_price": b.total_price,
        "original_price": b.original_price,
        "discount_amount": b.discount_amount,
        "status": b.status,
        "created_at": b.created_at.strftime("%Y-%m-%d %H:%M") if b.created_at else ""
    } for b in bookings]

# ==============================================================================
# PROMOTIONS
# ==============================================================================
@app.get("/api/promotions")
def get_promotions(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    promos = db.query(models.Promotion).filter(models.Promotion.is_active == True).all()
    return [{
        "id": p.id, "code": p.code, "title": p.title, "description": p.description,
        "discount_percent": p.discount_percent,
        "valid_from": p.valid_from.strftime("%Y-%m-%d") if p.valid_from else "",
        "valid_until": p.valid_until.strftime("%Y-%m-%d") if p.valid_until else "",
        "remaining_uses": p.max_usage - p.current_usage,
        # is_valid: kiểm tra cả valid_from và valid_until
        "is_valid": (
            (not p.valid_from or p.valid_from <= now) and
            (not p.valid_until or p.valid_until >= now) and
            p.current_usage < p.max_usage
        ),
        "image_url": p.image_url
    } for p in promos]

@app.post("/api/promotions/apply")
def apply_promotion(data: PromoApply, db: Session = Depends(get_db)):
    promo = db.query(models.Promotion).filter(models.Promotion.code == data.code.upper(), models.Promotion.is_active == True).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promo not found")
    now = datetime.utcnow()
    if promo.valid_from and promo.valid_from > now:
        raise HTTPException(status_code=400, detail="Promo not yet active")
    if promo.valid_until and promo.valid_until < now:
        raise HTTPException(status_code=400, detail="Promo expired")
    if promo.current_usage >= promo.max_usage:
        raise HTTPException(status_code=400, detail="Promo maxed out")
    if data.total_price <= 0:
        raise HTTPException(status_code=400, detail="Invalid total price")
    discount = data.total_price * (promo.discount_percent / 100)
    return {
        "code": promo.code, "title": promo.title,
        "discount_percent": promo.discount_percent,
        "discount_amount": round(discount, 2),
        "original_price": data.total_price,
        "final_price": round(data.total_price - discount, 2)
    }

@app.post("/api/promotions/claim")
def claim_promotion(data: PromoClaim, db: Session = Depends(get_db)):
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Find promotion
    promo = db.query(models.Promotion).filter(
        models.Promotion.code == data.code.upper(),
        models.Promotion.is_active == True
    ).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promotion not found")
        
    # Check if already claimed
    existing = db.query(models.UserPromotion).filter(
        models.UserPromotion.user_id == data.user_id,
        models.UserPromotion.promotion_id == promo.id
    ).first()
    if existing:
        return {"status": "success", "message": "Promotion already claimed"}
        
    # Claim promotion
    new_claim = models.UserPromotion(user_id=data.user_id, promotion_id=promo.id)
    db.add(new_claim)
    db.commit()
    return {"status": "success", "message": "Promotion claimed successfully!"}

@app.get("/api/promotions/user/{user_id}")
def get_user_promotions(user_id: int, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    # Query claimed promotions via link table
    claimed = db.query(models.Promotion).join(
        models.UserPromotion,
        models.UserPromotion.promotion_id == models.Promotion.id
    ).filter(models.UserPromotion.user_id == user_id).all()
    
    return [{
        "id": p.id,
        "code": p.code,
        "title": p.title,
        "description": p.description,
        "discount_percent": p.discount_percent,
        "valid_from": p.valid_from.strftime("%Y-%m-%d") if p.valid_from else "",
        "valid_until": p.valid_until.strftime("%Y-%m-%d") if p.valid_until else "",
        "is_valid": (
            (not p.valid_from or p.valid_from <= now) and
            (not p.valid_until or p.valid_until >= now) and
            p.current_usage < p.max_usage
        ),
        "image_url": p.image_url
    } for p in claimed]

# ==============================================================================
# UTILITIES
# ==============================================================================
@app.get("/languages")
def get_languages():
    data = rapidapi_get("/languages", {})
    if data and "data" in data:
        return data["data"]
    # Fallback if API fails
    return [{"name": "Tiếng Việt", "code": "vi-vn"}, {"name": "English", "code": "en-us"}]

@app.get("/currencies")
def get_currencies():
    data = rapidapi_get("/currencies", {})
    if data and "AllCurrencyList" in data:
        return data["AllCurrencyList"]
    # Fallback if API fails
    return [{"name": "Viet Nam Dong", "code": "VND"}, {"name": "US Dollar", "code": "USD"}]

# ==============================================================================
