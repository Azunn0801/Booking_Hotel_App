import os
import re
import shutil

# Directories
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_AGODA_DIR = os.path.join(WORKSPACE_DIR, "resources_web", "agoda")
SRC_YCS_DIR = os.path.join(WORKSPACE_DIR, "resources_web", "YCS")
DEST_TEMPLATES_DIR = os.path.join(WORKSPACE_DIR, "web_platform", "templates")

os.makedirs(DEST_TEMPLATES_DIR, exist_ok=True)

# Mappings (source file name in resources_web -> destination name in web_platform/templates)
TEMPLATES_MAPPING = [
    {
        "src_dir": SRC_AGODA_DIR,
        "src_file": "Trang Web Chính Thức Của Agoda _ Miễn Phí Hủy & Ưu Đãi Đặt Phòng _ Hơn 2 Triệu Khách Sạn.html",
        "dest_file": "index.html",
        "type": "index"
    },
    {
        "src_dir": SRC_AGODA_DIR,
        "src_file": "Agoda _ Khách sạn ở Vũng Tàu _ Đảm bảo giá tốt nhất.html",
        "dest_file": "search.html",
        "type": "search"
    },
    {
        "src_dir": SRC_AGODA_DIR,
        "src_file": "Khách sạn căn hộ Vy Vân (HOTEL & APARTMENT VY VAN) Vũng Tàu, Việt Nam_ Agoda.com có giá rẻ nhất.html",
        "dest_file": "detail.html",
        "type": "detail"
    },
    {
        "src_dir": SRC_AGODA_DIR,
        "src_file": "Hồ sơ.html",
        "dest_file": "profile.html",
        "type": "profile"
    },
    {
        "src_dir": SRC_AGODA_DIR,
        "src_file": "Mã khuyến mại Agoda_ Chiết khấu + Phiếu giảm giá cho khách sạn được cập nhật hàng ngày.html",
        "dest_file": "deals.html",
        "type": "deals"
    },
    {
        "src_dir": SRC_YCS_DIR,
        "src_file": "Nhà và Khách sạn Agoda_ Đăng cơ sở lưu trú của quý đối tác và bắt đầu kiếm thu nhập ngay hôm nay!.html",
        "dest_file": "list_property.html",
        "type": "list_property"
    },
    {
        "src_dir": SRC_YCS_DIR,
        "src_file": "YCS - Mạng diện rộng đối tác.html",
        "dest_file": "ycs_portal.html",
        "type": "ycs_portal"
    },
    {
        "src_dir": SRC_YCS_DIR,
        "src_file": "89491401.html",
        "dest_file": "ycs_dashboard.html",
        "type": "ycs_dashboard"
    },
    {
        "src_dir": SRC_AGODA_DIR,
        "src_file": "agodacash.html",
        "dest_file": "agodacash.html",
        "type": "profile_subpage"
    },
    {
        "src_dir": SRC_AGODA_DIR,
        "src_file": "cashback.html",
        "dest_file": "cashback.html",
        "type": "profile_subpage"
    },
    {
        "src_dir": SRC_AGODA_DIR,
        "src_file": "inbox.html",
        "dest_file": "inbox.html",
        "type": "profile_subpage"
    },
    {
        "src_dir": SRC_AGODA_DIR,
        "src_file": "pointsmax.html",
        "dest_file": "pointsmax.html",
        "type": "profile_subpage"
    },
    {
        "src_dir": SRC_AGODA_DIR,
        "src_file": "reviews.html",
        "dest_file": "reviews.html",
        "type": "profile_subpage"
    },
    {
        "src_dir": SRC_AGODA_DIR,
        "src_file": "submit.html",
        "dest_file": "submit.html",
        "type": "submit_review"
    },
    {
        "src_dir": SRC_AGODA_DIR,
        "src_file": "vip.html",
        "dest_file": "vip.html",
        "type": "profile_subpage"
    },
    {
        "src_dir": SRC_AGODA_DIR,
        "src_file": "Chuyến đi.html",
        "dest_file": "trips.html",
        "type": "trips"
    },
    {
        "src_dir": SRC_AGODA_DIR,
        "src_file": "Đơn đặt phòng.html",
        "dest_file": "bookings_list.html",
        "type": "bookings_list"
    },
    {
        "src_dir": SRC_AGODA_DIR,
        "src_file": "Agoda - Chi tiết đơn đặt chỗ khách sạn.html",
        "dest_file": "booking_detail.html",
        "type": "booking_detail"
    }
]

def replace_html_block(html, start_marker, replacement):
    idx = html.find(start_marker)
    if idx == -1:
        return html
    
    open_divs = 1
    current_idx = idx + len(start_marker)
    while open_divs > 0 and current_idx < len(html):
        next_open = html.find("<div", current_idx)
        next_close = html.find("</div>", current_idx)
        
        if next_close == -1:
            break
            
        if next_open != -1 and next_open < next_close:
            open_divs += 1
            current_idx = next_open + 4
        else:
            open_divs -= 1
            current_idx = next_close + 6
            
    if open_divs == 0:
        return html[:idx] + replacement + html[current_idx:]
    return html

def clean_tracking_scripts(html):
    # Strip tracking scripts (GTM, Google Analytics, FB pixel, etc.)
    html = re.sub(r'<script[^>]*src="[^"]*gtm\.js[^"]*"[^>]*></script>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<script[^>]*src="[^"]*analytics\.js[^"]*"[^>]*></script>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<iframe[^>]*src="[^"]*googletagmanager\.com[^"]*"[^>]*></iframe>', '', html, flags=re.IGNORECASE)
    # Also strip agoda external scripts that block rendering
    html = re.sub(r'<script[^>]*src="https://www\.agoda\.com/[^"]*"[^>]*></script>', '', html, flags=re.IGNORECASE)
    return html

# Define the Jinja injected profile menu
JINJA_USER_MENU = """
<div class="Box-sc-kv6pi1-0 flviCy" bis_skin_checked="1">
    <% if user %>
    <div style="display: flex; align-items: center; gap: 10px; position: relative;">
        <!-- ... existing menu items ... -->
        <a href="/ycs" style="padding: 6px 12px; background: #e57237; color: white; border-radius: 4px; text-decoration: none; font-size: 14px; font-weight: bold; margin-right: 15px;">Kênh đối tác (YCS)</a>
        
        <div id="user-menu-trigger" style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 5px 10px; border-radius: 20px; border: 1px solid #ddd; background: white;">
            <div style="width: 32px; height: 32px; background-color: #5392f9; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">
                <%= user.full_name[0] | upper %>
            </div>
            <div style="display: flex; flex-direction: column;">
                <span style="font-weight: bold; font-size: 14px; color: #333;"><%= user.full_name %></span>
                <span style="font-size: 12px; color: #777;"><%= user.email %></span>
            </div>
        </div>

        <div id="user-dropdown" style="display: none; position: absolute; top: 45px; right: 0; background: white; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); width: 250px; z-index: 1000; overflow: hidden;">
            <a href="/agodacash" style="display: block; padding: 12px 16px; color: #333; text-decoration: none; border-bottom: 1px solid #eee; font-size: 14px;">AgodaCash</a>
            <a href="/vip" style="display: block; padding: 12px 16px; color: #333; text-decoration: none; border-bottom: 1px solid #eee; font-size: 14px;">AgodaVIP</a>
            <a href="/bookings" style="display: block; padding: 12px 16px; color: #333; text-decoration: none; border-bottom: 1px solid #eee; font-size: 14px;">Đơn đặt phòng</a>
            <a href="/trips" style="display: block; padding: 12px 16px; color: #333; text-decoration: none; border-bottom: 1px solid #eee; font-size: 14px;">Chuyến đi</a>
            <a href="/inbox" style="display: block; padding: 12px 16px; color: #333; text-decoration: none; border-bottom: 1px solid #eee; font-size: 14px;">Hộp thư</a>
            <a href="/reviews" style="display: block; padding: 12px 16px; color: #333; text-decoration: none; border-bottom: 1px solid #eee; font-size: 14px;">Nhận xét</a>
            <a href="/logout" style="display: block; padding: 12px 16px; color: #e22b35; text-decoration: none; font-size: 14px; font-weight: bold; background: #fdf5f5;">Đăng xuất</a>
        </div>
    </div>
    
    <script>
        document.getElementById('user-menu-trigger').addEventListener('click', function() {
            var dropdown = document.getElementById('user-dropdown');
            dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
        });
        document.addEventListener('click', function(e) {
            if (!document.getElementById('user-menu-trigger').contains(e.target) && !document.getElementById('user-dropdown').contains(e.target)) {
                document.getElementById('user-dropdown').style.display = 'none';
            }
        });
    </script>
    <% else %>
    <button type="button" class="Button-sc-1j23htv-0 eXwDmb" onclick="window.location.href='/list-property/register'">Đăng chỗ nghỉ</button>
    <button type="button" class="Button-sc-1j23htv-0 hLWeis" onclick="window.location.href='/login?next=<%= request.url._url %>'"><span class="Span-sc-1mw2e2b-0 hYhYqW"><span class="Span-sc-1mw2e2b-0 kOIKjV">Đăng nhập</span></span></button>
    <button type="button" class="Button-sc-1j23htv-0 jLccmG" onclick="window.location.href='/login?next=<%= request.url._url %>'"><span class="Span-sc-1mw2e2b-0 hYhYqW"><span class="Span-sc-1mw2e2b-0 kOIKjV">Tạo tài khoản</span></span></button>
    <% endif %>
</div>
"""

# Header YCS Portal Menu Replacement
JINJA_YCS_HEADER = """
<div style="display: flex; align-items: center; gap: 12px;">
  <div style="color: white; font-weight: 600;"><%= user.full_name %></div>
  <a href="/auth/logout" onclick="event.preventDefault(); logout();" style="color: #ffaa00; text-decoration: none; font-weight: bold; font-size: 13px;">Đăng xuất</a>
</div>
<script>
  function logout() {
    fetch('/auth/logout', { method: 'POST' })
      .then(res => res.json())
      .then(() => window.location.href = '/');
  }
</script>
"""

def clean_template_file(t):
    src_path = os.path.join(t["src_dir"], t["src_file"])
    dest_path = os.path.join(DEST_TEMPLATES_DIR, t["dest_file"])
    
    print(f"Processing -> {t['dest_file']}...")
    
    if not os.path.exists(src_path):
        print(f"WARNING: Source file for {t['dest_file']} does not exist!")
        return

    with open(src_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Apply tracking cleanses
    html = clean_tracking_scripts(html)

    # Process based on type
    if t["type"] in ["index", "search", "detail", "profile", "deals", "profile_subpage", "submit_review", "trips", "bookings_list", "booking_detail"]:
        # Apply header profile injection
        html = replace_html_block(html, '<div class="Box-sc-kv6pi1-0 flviCy" bis_skin_checked="1">', JINJA_USER_MENU)

    # Define Shared Search Widget Custom JS (Autocomplete & Calendar)
    shared_search_widget_js = """
    <script>
    document.addEventListener('DOMContentLoaded', () => {
            const todayStr = new Date().toISOString().split('T')[0];
            const formatDate = (d) => d.toISOString().split('T')[0];

            let searchString = window.location.search.replace(/&amp;/g, '&').replace(/amp;/g, '');
            const urlParams = new URLSearchParams(searchString);
            
            let cityId = urlParams.get('city_id') || "1_17190"; // default Vũng Tàu
            let destinationName = urlParams.get('destination') || "Vũng Tàu";
            
            // Format dates cleanly, default to tomorrow and day after tomorrow
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            const dayAfter = new Date();
            dayAfter.setDate(dayAfter.getDate() + 2);
            
            let checkin = urlParams.get('checkin') || formatDate(tomorrow);
            let checkout = urlParams.get('checkout') || formatDate(dayAfter);
            
            // Replace any spaces or underscores with dashes
            checkin = checkin.replace(/[\s_]+/g, '-');
            checkout = checkout.replace(/[\s_]+/g, '-');
            
            // Adjust if dates are in the past
            if (checkin < todayStr) {
                checkin = todayStr;
            }
            if (checkout <= checkin) {
                const nextDay = new Date(checkin);
                nextDay.setDate(nextDay.getDate() + 1);
                checkout = formatDate(nextDay);
            }
            
            let propertyType = urlParams.get('property_type') || "hotel";
            let bookingType = urlParams.get('booking_type') || "overnight";
            let adults = urlParams.get('adult') || urlParams.get('adults') || "2";
            let rooms = urlParams.get('rooms') || urlParams.get('room') || "1";

            // Support multiple inputs sync
            const destInputs = document.querySelectorAll('[data-selenium="textInput"], #textInput');
            
            destInputs.forEach(destInput => {
                if (window.location.pathname === '/') {
                    destInput.value = "";
                } else {
                    destInput.value = destinationName;
                }
                destInput.placeholder = "Nhập điểm du lịch hoặc tên khách sạn...";
                
                const acDropdown = document.createElement('div');
                acDropdown.style.cssText = "position:absolute; background:white; border:1px solid #ddd; border-radius:8px; box-shadow:0 4px 12px rgba(0,0,0,0.15); max-height:300px; overflow-y:auto; z-index:999999; display:none; text-align:left;";
                document.body.appendChild(acDropdown);
                
                const updateDropdownPosition = () => {
                    const rect = destInput.getBoundingClientRect();
                    acDropdown.style.top = (rect.bottom + window.scrollY + 5) + 'px';
                    acDropdown.style.left = (rect.left + window.scrollX) + 'px';
                    acDropdown.style.width = rect.width + 'px';
                };

                window.addEventListener('resize', () => {
                    if (acDropdown.style.display === 'block') updateDropdownPosition();
                });

                let timeout;
                destInput.addEventListener('input', (e) => {
                    clearTimeout(timeout);
                    const q = e.target.value.trim();
                    if (q.length < 2) {
                        acDropdown.style.display = 'none';
                        return;
                    }
                    timeout = setTimeout(async () => {
                        const res = await fetch(`/hotels/auto-complete?q=${encodeURIComponent(q)}`);
                        const data = await res.json();
                        if (!data || data.length === 0) {
                            acDropdown.style.display = 'none';
                            return;
                        }
                        acDropdown.innerHTML = '';
                        data.forEach(item => {
                            const div = document.createElement('div');
                            div.style.cssText = "padding:10px 16px; cursor:pointer; border-bottom:1px solid #f0f0f0; display:flex; align-items:center; gap:10px;";
                            div.innerHTML = `<span>📍</span><div><div style="font-weight:600; color:#333; font-size:13px;">${item.name}</div><div style="font-size:11px; color:#888;">${item.country || ''}</div></div>`;
                            
                            div.addEventListener('mouseover', () => div.style.backgroundColor = '#f4f8ff');
                            div.addEventListener('mouseout', () => div.style.backgroundColor = 'transparent');

                            div.addEventListener('mousedown', (ev) => {
                                ev.preventDefault();
                                
                                // Sync all input elements values
                                destInputs.forEach(inp => inp.value = item.name);
                                
                                cityId = item.city_id || item.id;
                                if (!cityId.toString().includes('_')) {
                                    cityId = "1_" + cityId;
                                }
                                destinationName = item.name;
                                acDropdown.style.display = 'none';
                            });
                            acDropdown.appendChild(div);
                        });
                        updateDropdownPosition();
                        acDropdown.style.display = 'block';
                    }, 250);
                });
                
                destInput.addEventListener('blur', () => {
                    setTimeout(() => { acDropdown.style.display = 'none'; }, 200);
                });
                destInput.addEventListener('focus', () => {
                    if (destInput.value.trim().length >= 2 && acDropdown.innerHTML !== '') {
                        updateDropdownPosition();
                        acDropdown.style.display = 'block';
                    }
                });
                destInput.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        const btn = document.querySelector('[data-selenium="searchButton"]') || document.querySelector('button[data-element-name="search-button"]');
                        if (btn) btn.click();
                    }
                });
            });

            const checkinBox = document.getElementById('check-in-box') || document.querySelector('[data-element-name="check-in-box"]');
            const checkoutBox = document.getElementById('check-out-box') || document.querySelector('[data-element-name="check-out-box"]');
            const occBox = document.getElementById('occupancy-box') || document.querySelector('[data-element-name="occupancy-box"]');
            
            let checkinInput, checkoutInput;
            
            if (checkinBox) {
                checkinBox.style.position = 'relative';
                checkinInput = document.createElement('input');
                checkinInput.type = 'date';
                checkinInput.value = checkin;
                checkinInput.min = todayStr;
                checkinInput.style.cssText = "position:absolute; top:0; left:0; width:100%; height:100%; opacity:0; cursor:pointer; z-index:9999;";
                checkinBox.appendChild(checkinInput);
            }

            if (checkoutBox) {
                checkoutBox.style.position = 'relative';
                checkoutInput = document.createElement('input');
                checkoutInput.type = 'date';
                checkoutInput.value = checkout;
                checkoutInput.min = checkin;
                checkoutInput.style.cssText = "position:absolute; top:0; left:0; width:100%; height:100%; opacity:0; cursor:pointer; z-index:9999;";
                checkoutBox.appendChild(checkoutInput);
            }

            const updateOccText = () => {
                if (occBox) {
                    const txtContainers = occBox.querySelectorAll('.IconBox__child div');
                    if (txtContainers.length > 0) {
                        txtContainers[0].innerHTML = `<span style="font-weight:bold; font-size:16px;">${adults} người lớn</span><br/><span style="color:#777; font-size:14px;">${rooms} phòng</span>`;
                    } else {
                        occBox.innerText = `${adults} người lớn, ${rooms} phòng`;
                    }
                }
            };

            const updateLabels = () => {
                if (checkinBox) {
                    const label = checkinBox.querySelector('.IconBox__child div') || checkinBox;
                    label.innerText = checkin;
                }
                if (checkoutBox) {
                    const label = checkoutBox.querySelector('.IconBox__child div') || checkoutBox;
                    label.innerText = checkout;
                }
                updateOccText();
            };

            updateLabels();

            if (checkinBox && checkinInput && checkoutInput) {
                checkinInput.addEventListener('change', (e) => {
                    checkin = e.target.value;
                    checkoutInput.min = checkin;
                    if (checkout <= checkin) {
                        const nextDay = new Date(checkin);
                        nextDay.setDate(nextDay.getDate() + 1);
                        checkout = formatDate(nextDay);
                        checkoutInput.value = checkout;
                    }
                    updateLabels();
                });
            }

            if (checkoutBox && checkoutInput) {
                checkoutInput.addEventListener('change', (e) => {
                    checkout = e.target.value;
                    updateLabels();
                });
            }

            const hotelTab = document.getElementById('tab-all-rooms-tab');
            const aptTab = document.getElementById('tab-home');
            if (hotelTab) {
                hotelTab.addEventListener('click', () => {
                    propertyType = "hotel";
                    document.querySelectorAll('li[role="tab"]').forEach(li => li.setAttribute('aria-selected', 'false'));
                    hotelTab.setAttribute('aria-selected', 'true');
                });
            }
            if (aptTab) {
                aptTab.addEventListener('click', () => {
                    propertyType = "apartment";
                    document.querySelectorAll('li[role="tab"]').forEach(li => li.setAttribute('aria-selected', 'false'));
                    aptTab.setAttribute('aria-selected', 'true');
                });
            }

            if (occBox) {
                const occDropdown = document.createElement('div');
                occDropdown.style.cssText = "position:absolute; background:white; border:1px solid #ddd; border-radius:8px; box-shadow:0 4px 12px rgba(0,0,0,0.15); padding:20px; z-index:999999; display:none; width: 300px; color: #333;";
                document.body.appendChild(occDropdown);

                occDropdown.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                        <span style="font-weight:600; font-size:15px;">Người lớn</span>
                        <div style="display:flex; align-items:center;">
                            <button id="adult-minus" style="width:36px; height:36px; border-radius:50%; border:1px solid #ccc; background:white; cursor:pointer; font-size:18px; display:flex; align-items:center; justify-content:center; color:#5392f9;">-</button>
                            <span id="adult-val" style="width:40px; text-align:center; font-weight:bold; font-size:16px;">${adults}</span>
                            <button id="adult-plus" style="width:36px; height:36px; border-radius:50%; border:1px solid #ccc; background:white; cursor:pointer; font-size:18px; display:flex; align-items:center; justify-content:center; color:#5392f9;">+</button>
                        </div>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:600; font-size:15px;">Phòng</span>
                        <div style="display:flex; align-items:center;">
                            <button id="room-minus" style="width:36px; height:36px; border-radius:50%; border:1px solid #ccc; background:white; cursor:pointer; font-size:18px; display:flex; align-items:center; justify-content:center; color:#5392f9;">-</button>
                            <span id="room-val" style="width:40px; text-align:center; font-weight:bold; font-size:16px;">${rooms}</span>
                            <button id="room-plus" style="width:36px; height:36px; border-radius:50%; border:1px solid #ccc; background:white; cursor:pointer; font-size:18px; display:flex; align-items:center; justify-content:center; color:#5392f9;">+</button>
                        </div>
                    </div>
                `;

                occDropdown.querySelector('#adult-minus').onclick = (e) => { e.preventDefault(); if(adults>1) { adults--; document.getElementById('adult-val').innerText=adults; updateOccText(); } };
                occDropdown.querySelector('#adult-plus').onclick = (e) => { e.preventDefault(); adults++; document.getElementById('adult-val').innerText=adults; updateOccText(); };
                occDropdown.querySelector('#room-minus').onclick = (e) => { e.preventDefault(); if(rooms>1) { rooms--; document.getElementById('room-val').innerText=rooms; updateOccText(); } };
                occDropdown.querySelector('#room-plus').onclick = (e) => { e.preventDefault(); rooms++; document.getElementById('room-val').innerText=rooms; updateOccText(); };

                occBox.style.cursor = 'pointer';
                occBox.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const rect = occBox.getBoundingClientRect();
                    occDropdown.style.top = (rect.bottom + window.scrollY + 10) + 'px';
                    occDropdown.style.left = (rect.left + window.scrollX) + 'px';
                    occDropdown.style.display = occDropdown.style.display === 'none' ? 'block' : 'none';
                });
                
                document.addEventListener('click', (e) => {
                    if (!occBox.contains(e.target) && !occDropdown.contains(e.target)) {
                        occDropdown.style.display = 'none';
                    }
                });
            }

            // Intercept form submissions containing search widget inputs to prevent raw submit
            document.addEventListener('submit', (e) => {
                const form = e.target;
                if (form.querySelector('[data-selenium="textInput"]') || form.querySelector('#textInput') || form.querySelector('[data-selenium="searchButton"]')) {
                    e.preventDefault();
                    triggerSearch();
                }
            });

            const searchBtns = document.querySelectorAll('[data-selenium="searchButton"], button[data-element-name="search-button"], button[data-element-name="search-button-sticky"]');
            searchBtns.forEach(btn => {
                btn.removeAttribute('onclick');
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    triggerSearch();
                });
            });

            function triggerSearch() {
                const mainInput = document.querySelector('[data-selenium="textInput"]') || document.getElementById('textInput');
                const queryDest = mainInput ? mainInput.value.trim() : destinationName;
                const path = window.location.pathname;
                
                let targetUrl = "";
                if (path.startsWith('/hotel/')) {
                    targetUrl = `${path}?checkin=${checkin}&checkout=${checkout}&adult=${adults}&rooms=${rooms}&property_type=${propertyType}&booking_type=${bookingType}`;
                } else {
                    targetUrl = `/search?city_id=${cityId}&destination=${encodeURIComponent(queryDest)}&checkin=${checkin}&checkout=${checkout}&property_type=${propertyType}&booking_type=${bookingType}&adult=${adults}&rooms=${rooms}`;
                }
                window.location.href = targetUrl;
            }
        });
        </script>
    """

        
    if t["type"] == "index":
        # 1. Clean destination input prefilled text
        html = html.replace('value="Joi Boutique Bãi Sau"', 'value=""')
        html = html.replace("</body>", shared_search_widget_js + "\n</body>")
    elif t["type"] == "search":
        html = html.replace('value="Vũng Tàu"', 'value=""')
        html = html.replace('value="Joi Boutique Bãi Sau"', 'value=""')
        # Xóa các đoạn script chứa src (ReactJS/NextJS của Agoda)
        html = re.sub(r'<script\b[^>]*src=[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        # Vô hiệu hóa script nhúng inline bằng cách xóa luôn chúng
        html = re.sub(r'<script\b(?![^>]*src=)[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        # Inject BOTH the autocomplete widget and the search results fetcher
        search_results_js = """
        <script>
        document.addEventListener('DOMContentLoaded', () => {
            let searchString = window.location.search.replace(/&amp;/g, '&').replace(/amp;/g, '');
            const urlParams = new URLSearchParams(searchString);
            const cityId = urlParams.get('city_id') || "1_2758";
            const cityName = urlParams.get('destination') || "Hà Nội";
            const checkin = urlParams.get('checkin') || new Date().toISOString().split('T')[0];
            const checkout = urlParams.get('checkout') || new Date(Date.now() + 86400000).toISOString().split('T')[0];
            const bookingType = urlParams.get('booking_type') || "overnight";
            const adult = urlParams.get('adult') || "2";
            const rooms = urlParams.get('rooms') || "1";
            let propertyTypeFilter = urlParams.get('property_type') || "";

            // Find hotel list container dynamically
            let listContainer = document.querySelector('.hotel-list-container');
            if (!listContainer) {
                const propertyCard = document.querySelector('.PropertyCard');
                if (propertyCard) listContainer = propertyCard.parentNode;
            }

            // Clone template card
            let originalCardTemplate = document.querySelector('.PropertyCardItem') || document.querySelector('[data-selenium="hotel-item"]');
            if (originalCardTemplate) {
                originalCardTemplate = originalCardTemplate.cloneNode(true);
            }

            // Helper function to search properties
            async function performSearch() {
                if (!listContainer) return;
                
                listContainer.innerHTML = `
                    <div style="text-align:center; padding:50px 20px; font-weight:600; color:#666;">
                        <img src="https://cdn6.agoda.net/images/brand/agoji-parachute.gif" style="width:60px;" /><br/>
                        Đang tìm kiếm chỗ nghỉ tốt nhất tại ${cityName}...
                    </div>
                `;

                // Collect checkbox filters
                let selectedStars = [];
                let selectedPropertyTypes = [];
                
                document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
                    if (cb.checked) {
                        const row = cb.closest('li') || cb.closest('.ab5c2-flex') || cb.parentElement.parentElement.parentElement.parentElement;
                        if (row) {
                            const labelEl = row.querySelector('[data-selenium="filter-item-text"]') || row.querySelector('span');
                            if (labelEl) {
                                const text = labelEl.innerText.trim().toLowerCase();
                                if (text.includes('sao') || text.includes('star')) {
                                    const starsMatch = text.match(/\\d+/);
                                    if (starsMatch) selectedStars.push(starsMatch[0]);
                                } else if (text.includes('khách sạn') || text.includes('hotel')) {
                                    selectedPropertyTypes.push('hotel');
                                } else if (text.includes('căn hộ') || text.includes('apartment') || text.includes('homestay')) {
                                    selectedPropertyTypes.push('apartment');
                                } else if (text.includes('biệt thự') || text.includes('villa')) {
                                    selectedPropertyTypes.push('villa');
                                } else if (text.includes('resort') || text.includes('khu nghỉ dưỡng')) {
                                    selectedPropertyTypes.push('resort');
                                }
                            }
                        }
                    }
                });

                // Collect price filters
                const minPriceEl = document.getElementById('price_box_0');
                const maxPriceEl = document.getElementById('price_box_1');
                const parsePrice = (str) => {
                    if (!str) return null;
                    const val = parseFloat(str.replace(/[.,\\s]/g, ''));
                    return isNaN(val) ? null : val;
                };
                const minPrice = minPriceEl ? parsePrice(minPriceEl.value) : null;
                const maxPrice = maxPriceEl ? parsePrice(maxPriceEl.value) : null;

                // Build query
                let queryParts = [
                    `city_id=${cityId}`,
                    `checkin=${checkin}`,
                    `checkout=${checkout}`,
                    `booking_type=${bookingType}`,
                    `adult=${adult}`,
                    `room=${rooms}`,
                    `limit=30`
                ];

                if (selectedStars.length > 0) {
                    queryParts.push(`star_rating=${selectedStars.join(',')}`);
                }
                
                if (selectedPropertyTypes.length > 0) {
                    queryParts.push(`property_type=${selectedPropertyTypes[0]}`); // Backend expects single property type
                } else if (propertyTypeFilter) {
                    queryParts.push(`property_type=${propertyTypeFilter}`);
                }

                if (minPrice !== null) {
                    queryParts.push(`min_price=${minPrice}`);
                }
                if (maxPrice !== null) {
                    queryParts.push(`max_price=${maxPrice}`);
                }

                const searchUrl = `/api/properties/search?` + queryParts.join('&');
                
                try {
                    const res = await fetch(searchUrl);
                    const hotels = await res.json();
                    
                    listContainer.innerHTML = '';
                    if (!hotels || hotels.length === 0) {
                        listContainer.innerHTML = '<div style="text-align:center; padding:40px; color:#666; font-weight:500;">Không tìm thấy chỗ nghỉ nào phù hợp.</div>';
                        return;
                    }

                    // Update header
                    const titleTextEl = document.querySelector('[data-element-name="properties-available-text"]');
                    if (titleTextEl) {
                        titleTextEl.innerText = `${hotels.length} cơ sở lưu trú tại ${cityName}`;
                    }

                    hotels.forEach(hotel => {
                        const detailUrl = `/hotel/${hotel.id}?checkin=${checkin}&checkout=${checkout}&adult=${adult}&rooms=${rooms}&booking_type=${bookingType}&fallback_name=${encodeURIComponent(hotel.name)}&fallback_city=${encodeURIComponent(hotel.city)}&fallback_image=${encodeURIComponent(hotel.imageUrl)}`;

                        if (originalCardTemplate) {
                            const cardNode = originalCardTemplate.cloneNode(true);
                            cardNode.querySelectorAll('a').forEach(a => a.href = detailUrl);
                            
                            cardNode.style.cursor = "pointer";
                            cardNode.onclick = (e) => {
                                if (!e.target.closest('button') && !e.target.closest('.Box-sc-kv6pi1-0')) {
                                    window.location.href = detailUrl;
                                }
                            };

                            const nameEl = cardNode.querySelector('[data-selenium="hotel-name"]') || cardNode.querySelector('h3');
                            if (nameEl) nameEl.innerText = hotel.name;

                            const scoreEl = cardNode.querySelector('[data-selenium="rating-value"]');
                            if (scoreEl) scoreEl.innerText = hotel.score.toFixed(1);

                            const reviewCountEl = cardNode.querySelector('[data-selenium="reviews-count"]');
                            if (reviewCountEl) reviewCountEl.innerText = `${hotel.reviewCount} nhận xét`;

                            const imgEl = cardNode.querySelector('img[src]');
                            if (imgEl) imgEl.src = hotel.imageUrl;
                            
                            const imgBgEl = cardNode.querySelector('[data-selenium="hotel-img"]') || cardNode.querySelector('.PropertyCardItem__Image');
                            if (imgBgEl && !imgEl) {
                                imgBgEl.style.backgroundImage = `url('${hotel.imageUrl}')`;
                            }

                            const priceEl = cardNode.querySelector('[data-selenium="display-price"]');
                            if (priceEl) priceEl.innerText = hotel.price.toLocaleString('vi-VN');
                            
                            const oriPriceEl = cardNode.querySelector('[data-selenium="crossed-out-price"]');
                            if (oriPriceEl) oriPriceEl.style.display = hotel.originalPrice > hotel.price ? 'inline-block' : 'none';
                            if (oriPriceEl && hotel.originalPrice > hotel.price) {
                                oriPriceEl.innerText = hotel.originalPrice.toLocaleString('vi-VN');
                            }

                            listContainer.appendChild(cardNode);
                        } else {
                            // Fallback premium template
                            const li = document.createElement('li');
                            li.style.cssText = "list-style:none; margin-bottom:20px; display:block; background:white; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.06); overflow:hidden; border:1px solid #e1e8ed;";
                            
                            const stars = '⭐'.repeat(Math.round(hotel.starRating || 3));
                            const discountBadge = hotel.discountPercent > 0 ? `<div style="background:#e22b35; color:white; font-size:11px; padding:3px 6px; border-radius:3px; font-weight:bold; display:inline-block; margin-bottom:5px;">-${hotel.discountPercent}%</div>` : '';
                            
                            li.innerHTML = `
                                <a href="${detailUrl}" style="text-decoration:none; color:inherit; display:flex; min-height:180px;">
                                    <div style="width:240px; background-image:url('${hotel.imageUrl}'); background-size:cover; background-position:center; position:relative; flex-shrink:0;"></div>
                                    <div style="padding:20px; flex:1; display:flex; justify-content:space-between; flex-direction:row;">
                                        <div style="display:flex; flex-direction:column; justify-content:space-between; text-align:left; flex:1; padding-right:15px;">
                                            <div>
                                                <span style="background:#f0f5ff; color:#0052cc; font-size:10px; font-weight:bold; padding:2px 6px; border-radius:3px; text-transform:uppercase;">${hotel.propertyTypeName || 'Khách sạn'}</span>
                                                <h3 style="font-size:18px; font-weight:bold; color:#1a3063; margin:6px 0 3px 0; line-height:1.3;">${hotel.name}</h3>
                                                <div style="color:#ffaa00; font-size:12px; margin-bottom:6px;">${stars}</div>
                                                <div style="color:#666; font-size:12px; margin-bottom:4px;">📍 ${hotel.address}, ${hotel.city}</div>
                                                <div style="color:#2e7d32; font-size:11px; font-weight:600;">✅ Hủy miễn phí phòng</div>
                                            </div>
                                        </div>
                                        <div style="width:180px; text-align:right; border-left:1px solid #eef2f5; padding-left:15px; display:flex; flex-direction:column; justify-content:space-between; align-items:flex-end;">
                                            <div style="display:flex; align-items:center; gap:8px;">
                                                <div style="text-align:right; line-height:1.2;">
                                                    <span style="font-weight:bold; font-size:13px;">${hotel.score >= 9 ? 'Trên cả tuyệt vời' : 'Tuyệt vời'}</span>
                                                    <div style="font-size:10px; color:#888;">${hotel.reviewCount} nhận xét</div>
                                                </div>
                                                <div style="background:#00aa6c; color:white; font-size:14px; font-weight:bold; padding:4px 8px; border-radius:6px;">${hotel.score.toFixed(1)}</div>
                                            </div>
                                            <div>
                                                ${discountBadge}
                                                <div style="font-size:10px; color:#888;">Giá mỗi đêm từ</div>
                                                ${hotel.originalPrice > hotel.price ? `<div style="text-decoration:line-through; color:#999; font-size:11px;">${hotel.originalPrice.toLocaleString('vi-VN')} đ</div>` : ''}
                                                <div style="font-size:20px; font-weight:800; color:#e57237; line-height:1;">${hotel.price.toLocaleString('vi-VN')} đ</div>
                                                <button style="background:#e57237; color:white; font-weight:bold; border:none; padding:8px 12px; border-radius:4px; font-size:12px; cursor:pointer; width:100%; margin-top:8px;">Xem phòng</button>
                                            </div>
                                        </div>
                                    </div>
                                </a>
                            `;
                            listContainer.appendChild(li);
                        }
                    });
                } catch(err) {
                    listContainer.innerHTML = '<div style="text-align:center; padding:40px; color:#e22b35;">Lỗi khi tải kết quả. Vui lòng thử lại.</div>';
                }
            }

            // Run initial search
            performSearch();

            // Set up check-box change event listeners
            setTimeout(() => {
                document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
                    cb.addEventListener('change', performSearch);
                });
                
                // Add listeners to price boxes
                const minPriceInput = document.getElementById('price_box_0');
                const maxPriceInput = document.getElementById('price_box_1');
                if (minPriceInput) {
                    minPriceInput.addEventListener('change', performSearch);
                    minPriceInput.addEventListener('blur', performSearch);
                    minPriceInput.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter') performSearch();
                    });
                }
                if (maxPriceInput) {
                    maxPriceInput.addEventListener('change', performSearch);
                    maxPriceInput.addEventListener('blur', performSearch);
                    maxPriceInput.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter') performSearch();
                    });
                }
            }, 1500); // Allow some time for layout to load completely
        });
        </script>
        """
        parts = html.rsplit("</body>", 1)
        if len(parts) == 2:
            html = parts[0] + search_results_js + "\n" + shared_search_widget_js + "\n</body>" + parts[1]
        else:
            html += search_results_js + "\n" + shared_search_widget_js

    elif t["type"] == "detail":
        # Inject dynamic Jinja variables and local room rendering logic into detail.html
        # Since room rendering is highly custom, we empty the scraped rooms section and inject our JS logic
        
        # Hide the react root initially to avoid flashing raw Vy Vân placeholders
        html = html.replace("<head>", '<head>\n<style>#home-react-root, #app-root { display: none; opacity: 0; }</style>')
        
        detail_js = """
        <script>
        document.addEventListener('DOMContentLoaded', () => {
            let searchString = window.location.search.replace(/&amp;/g, '&').replace(/amp;/g, '');
            const urlParams = new URLSearchParams(searchString);
            const pathParts = window.location.pathname.split('/');
            const hotelId = pathParts[pathParts.length - 1]; // Lấy ID trực tiếp từ URL
            
            const checkin = urlParams.get('checkin') || new Date().toISOString().split('T')[0];
            const checkout = urlParams.get('checkout') || new Date(Date.now() + 86400000).toISOString().split('T')[0];
            const adult = urlParams.get('adult') || "2";
            const roomsCount = urlParams.get('rooms') || "1";
            
            // Lấy các tham số dự phòng từ URL
            const fbName = urlParams.get('fallback_name') || "";
            const fbCity = urlParams.get('fallback_city') || "";
            const fbImg = urlParams.get('fallback_image') || "";
            
            // Create premium shimmer skeleton overlay
            const root = document.getElementById('home-react-root') || document.getElementById('app-root') || document.body;
            if (root) {
                // Style for skeleton shimmer
                const styleSkeleton = document.createElement('style');
                styleSkeleton.innerHTML = `
                    @keyframes shimmer {
                        0% { background-position: -468px 0; }
                        100% { background-position: 468px 0; }
                    }
                    .skeleton-shimmer {
                        background: #f6f7f8;
                        background-image: linear-gradient(to right, #f6f7f8 0%, #edeef1 20%, #f6f7f8 40%, #f6f7f8 100%);
                        background-repeat: no-repeat;
                        background-size: 800px 100%;
                        display: inline-block;
                        position: relative;
                        animation-duration: 1.2s;
                        animation-fill-mode: forwards;
                        animation-iteration-count: infinite;
                        animation-name: shimmer;
                        animation-timing-function: linear;
                    }
                `;
                document.head.appendChild(styleSkeleton);

                const skeleton = document.createElement('div');
                skeleton.id = 'agoda-detail-skeleton';
                skeleton.style.cssText = "max-width: 1200px; margin: 20px auto; padding: 20px; font-family: 'Inter', sans-serif; text-align: left;";
                skeleton.innerHTML = `
                    <!-- Breadcrumbs skeleton -->
                    <div class="skeleton-shimmer" style="width: 250px; height: 16px; border-radius: 4px; margin-bottom: 20px;"></div>
                    
                    <!-- Title & Rating skeleton -->
                    <div style="margin-bottom: 24px;">
                        <div class="skeleton-shimmer" style="width: 50%; height: 32px; border-radius: 6px; margin-bottom: 10px;"></div>
                        <div class="skeleton-shimmer" style="width: 100px; height: 16px; border-radius: 4px; margin-bottom: 8px;"></div>
                        <div class="skeleton-shimmer" style="width: 40%; height: 14px; border-radius: 4px;"></div>
                    </div>
                    
                    <!-- Gallery skeleton -->
                    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 8px; height: 400px; margin-bottom: 30px; border-radius: 12px; overflow: hidden;">
                        <div class="skeleton-shimmer" style="width: 100%; height: 100%;"></div>
                        <div style="display: grid; grid-template-rows: 1fr 1fr; gap: 8px; height: 100%;">
                            <div class="skeleton-shimmer" style="width: 100%; height: 100%;"></div>
                            <div class="skeleton-shimmer" style="width: 100%; height: 100%;"></div>
                        </div>
                    </div>
                    
                    <!-- Content Split: Description & Review summary -->
                    <div style="display: flex; gap: 30px; margin-bottom: 40px; flex-wrap: wrap;">
                        <div style="flex: 2; min-width: 300px;">
                            <div class="skeleton-shimmer" style="width: 150px; height: 24px; border-radius: 4px; margin-bottom: 15px;"></div>
                            <div class="skeleton-shimmer" style="width: 100%; height: 14px; border-radius: 4px; margin-bottom: 8px;"></div>
                            <div class="skeleton-shimmer" style="width: 95%; height: 14px; border-radius: 4px; margin-bottom: 8px;"></div>
                            <div class="skeleton-shimmer" style="width: 98%; height: 14px; border-radius: 4px; margin-bottom: 8px;"></div>
                            <div class="skeleton-shimmer" style="width: 80%; height: 14px; border-radius: 4px;"></div>
                        </div>
                        <div style="flex: 1; min-width: 250px; border: 1px solid #e1e8ed; border-radius: 8px; padding: 20px; display: flex; flex-direction: column; gap: 12px; height: fit-content;">
                            <div class="skeleton-shimmer" style="width: 100px; height: 20px; border-radius: 4px;"></div>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div class="skeleton-shimmer" style="width: 48px; height: 48px; border-radius: 8px;"></div>
                                <div style="flex: 1;">
                                    <div class="skeleton-shimmer" style="width: 80px; height: 16px; border-radius: 4px; margin-bottom: 6px;"></div>
                                    <div class="skeleton-shimmer" style="width: 60px; height: 12px; border-radius: 4px;"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Rooms Section Header -->
                    <div class="skeleton-shimmer" style="width: 200px; height: 28px; border-radius: 6px; margin-bottom: 20px;"></div>
                    
                    <!-- Room Cards Skeletons -->
                    <div style="display: flex; flex-direction: column; gap: 20px;">
                        <!-- Card 1 -->
                        <div style="display: flex; border: 1px solid #e1e8ed; border-radius: 12px; overflow: hidden; height: 220px; flex-wrap: wrap;">
                            <div class="skeleton-shimmer" style="width: 320px; height: 100%;"></div>
                            <div style="flex: 1; padding: 20px; display: flex; flex-direction: column; justify-content: space-between;">
                                <div>
                                    <div class="skeleton-shimmer" style="width: 60%; height: 22px; border-radius: 4px; margin-bottom: 12px;"></div>
                                    <div style="display: flex; gap: 8px; margin-bottom: 12px;">
                                        <div class="skeleton-shimmer" style="width: 60px; height: 20px; border-radius: 4px;"></div>
                                        <div class="skeleton-shimmer" style="width: 80px; height: 20px; border-radius: 4px;"></div>
                                    </div>
                                    <div class="skeleton-shimmer" style="width: 120px; height: 16px; border-radius: 4px;"></div>
                                </div>
                                <div style="display: flex; gap: 8px;">
                                    <div class="skeleton-shimmer" style="width: 100px; height: 20px; border-radius: 4px;"></div>
                                    <div class="skeleton-shimmer" style="width: 100px; height: 20px; border-radius: 4px;"></div>
                                </div>
                            </div>
                            <div style="width: 220px; padding: 20px; background: #fafbfc; border-left: 1px solid #e1e8ed; display: flex; flex-direction: column; justify-content: space-between; align-items: flex-end;">
                                <div style="text-align: right; width: 100%;">
                                    <div class="skeleton-shimmer" style="width: 80px; height: 12px; border-radius: 4px; margin-left: auto; margin-bottom: 6px;"></div>
                                    <div class="skeleton-shimmer" style="width: 120px; height: 24px; border-radius: 4px; margin-left: auto;"></div>
                                </div>
                                <div class="skeleton-shimmer" style="width: 100%; height: 40px; border-radius: 6px;"></div>
                            </div>
                        </div>
                    </div>
                `;
                root.parentNode.insertBefore(skeleton, root);
            }

            // Fetch details and rooms in parallel
            const detailsPromise = fetch(`/api/properties/${hotelId}/details?checkin=${checkin}&checkout=${checkout}&fallback_name=${encodeURIComponent(fbName)}&fallback_city=${encodeURIComponent(fbCity)}&fallback_image=${encodeURIComponent(fbImg)}`)
            .then(res => {
                if (!res.ok) throw new Error("API error details");
                return res.json();
            });
            
            const roomsPromise = fetch(`/api/properties/${hotelId}/rooms?checkin=${checkin}&checkout=${checkout}&adult=${adult}&room=${roomsCount}`)
            .then(res => {
                if (!res.ok) throw new Error("API error rooms");
                return res.json();
            });

            // Set up room carousel global functions
            window.roomCarousels = {};
            window.roomCarouselIndices = {};
            window.rotateCarousel = function(roomId, direction) {
                const images = window.roomCarousels[roomId] || [];
                if (images.length <= 1) return;
                let currentIdx = window.roomCarouselIndices[roomId] || 0;
                currentIdx = (currentIdx + direction + images.length) % images.length;
                window.setCarouselSlide(roomId, currentIdx);
            };
            window.setCarouselSlide = function(roomId, slideIdx) {
                window.roomCarouselIndices[roomId] = slideIdx;
                const card = document.getElementById(`room-card-${roomId}`);
                if (!card) return;
                const slides = card.querySelector('.room-carousel-slides');
                if (slides) {
                    slides.style.transform = `translateX(-${slideIdx * 100}%)`;
                }
                const dots = card.querySelectorAll('.carousel-dot');
                dots.forEach((dot, idx) => {
                    dot.style.background = idx === slideIdx ? '#fff' : 'rgba(255,255,255,0.5)';
                    dot.style.width = idx === slideIdx ? '10px' : '8px';
                    dot.style.height = idx === slideIdx ? '10px' : '8px';
                });
            };

            // Inject CSS for dynamic cards
            const style = document.createElement('style');
            style.innerHTML = `
                .agoda-rooms-grid {
                    display: grid;
                    grid-template-columns: 1fr;
                    gap: 20px;
                    margin-top: 20px;
                }
                .agoda-room-card {
                    background: #ffffff;
                    border: 1px solid #e1e8ed;
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
                    overflow: hidden;
                    margin-bottom: 20px;
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                    display: flex;
                    flex-direction: column;
                }
                @media (min-width: 768px) {
                    .agoda-room-card {
                        flex-direction: row;
                    }
                }
                .agoda-room-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
                }
                .room-image-section {
                    width: 100%;
                    position: relative;
                }
                @media (min-width: 768px) {
                    .room-image-section {
                        width: 320px;
                        flex-shrink: 0;
                    }
                }
                @media (max-width: 767px) {
                    .room-image-section {
                        height: 200px;
                    }
                }
                .room-details-section {
                    flex: 1;
                    padding: 20px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    border-right: 1px solid #eef2f5;
                }
                @media (max-width: 767px) {
                    .room-details-section {
                        border-right: none;
                        border-bottom: 1px solid #eef2f5;
                    }
                }
                .room-pricing-section {
                    width: 100%;
                    padding: 20px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    align-items: center;
                    background: #fafbfc;
                }
                @media (min-width: 768px) {
                    .room-pricing-section {
                        width: 220px;
                        flex-shrink: 0;
                        align-items: flex-end;
                    }
                }
                .amenity-chip {
                    display: inline-block;
                    background: #f0f3f6;
                    color: #4a5568;
                    font-size: 11px;
                    font-weight: 500;
                    padding: 4px 8px;
                    border-radius: 4px;
                    margin-right: 6px;
                    margin-bottom: 6px;
                }
                .badge-breakfast {
                    background: #e6f7ed;
                    color: #2e7d32;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 4px 8px;
                    border-radius: 4px;
                    display: inline-flex;
                    align-items: center;
                    gap: 4px;
                }
                .badge-cancellation {
                    background: #e3f2fd;
                    color: #1565c0;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 4px 8px;
                    border-radius: 4px;
                    display: inline-flex;
                    align-items: center;
                    gap: 4px;
                }
                .badge-urgency {
                    background: #ffebee;
                    color: #c62828;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 4px 8px;
                    border-radius: 4px;
                    display: inline-flex;
                    align-items: center;
                    gap: 4px;
                }
            `;
            document.head.appendChild(style);

            Promise.all([detailsPromise, roomsPromise])
            .then(([data, rooms]) => {
                // Populate details
                document.title = data.name + " | Agoda Clone";
                
                document.querySelectorAll('input[type="text"]').forEach(inp => {
                    if (inp.value && (inp.value.includes('Vy Vân') || inp.value.includes('VY VAN'))) {
                        inp.value = data.name;
                    }
                });

                const breadcrumbs = document.querySelectorAll('[data-selenium="breadcrumb-item"]');
                if (breadcrumbs.length > 0) breadcrumbs[breadcrumbs.length - 1].innerText = data.name;
                const regionName = document.querySelector('p.breadcrumb-regionName');
                if (regionName) regionName.innerText = data.name;

                const h1Node = document.querySelector('h1[data-selenium="hotel-header-name"]') || document.querySelector('h1');
                if (h1Node) h1Node.innerText = data.name;

                document.querySelectorAll('.StarRating, [data-selenium="star-rating"], i[class*="star"]').forEach(star => {
                    star.innerHTML = '★'.repeat(Math.round(data.starRating));
                });

                const addressNode = document.querySelector('[data-selenium="hotel-address-map"]');
                if (addressNode) addressNode.innerText = `${data.address.street}, ${data.address.city}, ${data.address.country}`;

                if (data.imageUrls && data.imageUrls.length > 0) {
                    const allImages = document.querySelectorAll('img[src]');
                    let imgIdx = 0;
                    allImages.forEach(img => {
                        if (img.width > 100 || img.className.includes('ImageStyled') || img.src.includes('agoda.net/images')) {
                            img.src = data.imageUrls[imgIdx % data.imageUrls.length].url;
                            img.srcset = "";
                            imgIdx++;
                        }
                    });
                }

                const descNode = document.querySelector('[data-selenium="hotel-description"]');
                if (descNode) descNode.innerText = data.description;

                // Populate rooms
                const gridRoot = document.getElementById('property-room-grid-root');
                if (gridRoot) {
                    Array.from(gridRoot.children).forEach(child => {
                        child.style.display = 'none';
                    });

                    const roomsSection = document.createElement('div');
                    roomsSection.id = 'agoda-rooms-custom-section';
                    roomsSection.style.cssText = "width:100%; text-align:left; padding: 20px 0;";
                    roomsSection.innerHTML = '<h2 style="color:#1a3063; font-weight:bold; font-size:22px; margin-bottom:20px;">Các loại phòng trống</h2>';

                    const grid = document.createElement('div');
                    grid.className = 'agoda-rooms-grid';
                    roomsSection.appendChild(grid);
                    gridRoot.appendChild(roomsSection);

                    rooms.forEach(room => {
                        window.roomCarousels[room.id] = room.images || [room.imageUrl];
                        window.roomCarouselIndices[room.id] = 0;

                        const card = document.createElement('div');
                        card.className = 'agoda-room-card';
                        card.id = `room-card-${room.id}`;

                        const imagesList = room.images || [room.imageUrl];
                        const carouselHtml = `
                            <div class="room-carousel" style="position: relative; width: 100%; height: 200px; overflow: hidden; border-radius: 8px 8px 0 0;">
                                <div class="room-carousel-slides" style="display: flex; transition: transform 0.3s ease; height: 100%;">
                                    ${imagesList.map(img => `
                                        <img src="${img}" style="width: 100%; height: 100%; object-fit: cover; flex-shrink: 0;" />
                                    `).join('')}
                                </div>
                                ${imagesList.length > 1 ? `
                                    <button class="carousel-arrow left" onclick="event.stopPropagation(); rotateCarousel('${room.id}', -1)" style="position: absolute; left: 10px; top: 50%; transform: translateY(-50%); background: rgba(0,0,0,0.5); color: white; border: none; border-radius: 50%; width: 30px; height: 30px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 16px; z-index: 10;">‹</button>
                                    <button class="carousel-arrow right" onclick="event.stopPropagation(); rotateCarousel('${room.id}', 1)" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: rgba(0,0,0,0.5); color: white; border: none; border-radius: 50%; width: 30px; height: 30px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 16px; z-index: 10;">›</button>
                                    <div class="carousel-dots" style="position: absolute; bottom: 10px; left: 50%; transform: translateX(-50%); display: flex; gap: 6px; z-index: 10;">
                                        ${imagesList.map((_, idx) => `
                                            <span class="carousel-dot ${idx === 0 ? 'active' : ''}" onclick="event.stopPropagation(); setCarouselSlide('${room.id}', ${idx})" style="width: 8px; height: 8px; border-radius: 50%; background: ${idx === 0 ? '#fff' : 'rgba(255,255,255,0.5)'}; cursor: pointer; display: inline-block;"></span>
                                        `).join('')}
                                    </div>
                                ` : ''}
                            </div>
                        `;

                        const amenitiesHtml = room.amenities.split(',').map(a => `<span class="amenity-chip">${a.trim()}</span>`).join('');
                        const capacityHtml = `👥 Tối đa ${room.occupancy.maxAdults || 2} người lớn${room.occupancy.maxChildren ? `, ${room.occupancy.maxChildren} trẻ em` : ''}`;
                        const breakfastHtml = room.breakfastIncluded ? `<span class="badge-breakfast">☕ Ăn sáng miễn phí</span>` : `<span class="amenity-chip">Không gồm ăn sáng</span>`;
                        const cancellationHtml = room.isFreeCancellation ? `<span class="badge-cancellation">✓ Hủy miễn phí</span>` : `<span class="badge-urgency" style="background:#f5f5f5; color:#777;">Không hoàn tiền</span>`;
                        const urgencyHtml = room.remainRoom <= 3 ? `<span class="badge-urgency">🔥 Chỉ còn ${room.remainRoom} phòng!</span>` : '';
                        const originalPriceHtml = room.originalPrice > room.price ? `<div style="text-decoration: line-through; color: #a0aec0; font-size: 12px; margin-bottom: 2px;">${room.originalPrice.toLocaleString('vi-VN')} ₫</div>` : '';
                        
                        card.innerHTML = `
                            <div class="room-image-section">${carouselHtml}</div>
                            <div class="room-details-section">
                                <div>
                                    <h3 style="font-size: 18px; font-weight: bold; color: #1a3063; margin-top: 0; margin-bottom: 8px;">${room.roomName}</h3>
                                    <div style="margin-bottom: 12px; display: flex; flex-wrap: wrap;">${amenitiesHtml}</div>
                                    <div style="color: #4a5568; font-size: 13px; font-weight: 500; display: flex; align-items: center; gap: 6px; margin-bottom: 12px;">${capacityHtml}</div>
                                </div>
                                <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px;">
                                    ${breakfastHtml}
                                    ${cancellationHtml}
                                    ${urgencyHtml}
                                </div>
                            </div>
                            <div class="room-pricing-section">
                                <div style="text-align: right; width: 100%;">
                                    <div style="font-size: 11px; color: #718096; margin-bottom: 4px;">Giá mỗi đêm từ</div>
                                    ${originalPriceHtml}
                                    <div style="font-size: 24px; font-weight: 800; color: #e57237; line-height: 1;">${room.price.toLocaleString('vi-VN')} ₫</div>
                                    <div style="font-size: 11px; color: #a0aec0; margin-top: 4px;">Chưa gồm thuế & phí</div>
                                </div>
                                <button onclick="bookRoom('${room.id}', '${room.roomName}', ${room.price}, '${room.imageUrl}')" style="background: #e57237; color: white; border: none; padding: 12px 20px; border-radius: 6px; font-weight: bold; font-size: 14px; width: 100%; cursor: pointer; text-align: center; box-shadow: 0 4px 12px rgba(229,114,55,0.2); transition: background 0.2s ease; margin-top: 15px;">Đặt ngay</button>
                            </div>
                        `;

                        grid.appendChild(card);
                    });
                }

                // Show main container and remove skeleton
                const skeleton = document.getElementById('agoda-detail-skeleton');
                if (skeleton) {
                    skeleton.style.transition = 'opacity 0.3s ease';
                    skeleton.style.opacity = '0';
                    setTimeout(() => {
                        skeleton.remove();
                        if (root) {
                            root.style.display = 'block';
                            root.style.opacity = '0';
                            root.style.transition = 'opacity 0.4s ease';
                            root.offsetHeight; // trigger reflow
                            root.style.opacity = '1';
                        }
                    }, 300);
                } else {
                    if (root) {
                        root.style.display = 'block';
                        root.style.opacity = '1';
                    }
                }
            })
            .catch(err => {
                console.error(err);
                const skeleton = document.getElementById('agoda-detail-skeleton');
                if (skeleton) skeleton.remove();
                if (root) {
                    root.style.display = 'block';
                    root.style.opacity = '1';
                }
            });
        });

        function bookRoom(roomId, roomName, price, imageUrl) {
            const currentUserId = <%= user.id if user else 'null' %>;
            if (!currentUserId) {
                alert("Vui lòng đăng nhập để thực hiện đặt phòng!");
                window.location.href = "/login?next=" + encodeURIComponent(window.location.pathname + window.location.search);
                return;
            }
            const idVal = currentUserId;
            
            let searchString = window.location.search.replace(/&amp;/g, '&').replace(/amp;/g, '');
            const params = new URLSearchParams(searchString);
            const checkin = (params.get('checkin') || new Date().toISOString().split('T')[0]).replace(/[\s_]+/g, '-');
            const checkout = (params.get('checkout') || new Date(Date.now() + 86400000).toISOString().split('T')[0]).replace(/[\s_]+/g, '-');
            
            const date1 = new Date(checkin);
            const date2 = new Date(checkout);
            const nights = Math.max(1, Math.round((date2 - date1)/(1000*60*60*24)));
            const totalPrice = price * nights;
            
            const hotelName = document.title.split(' | ')[0] || "Khách sạn";
            
            const bookingData = {
                user_id: parseInt(idVal),
                property_id: "${hotelId}",
                property_name: hotelName + " - " + roomName,
                property_type: "hotel",
                property_image: imageUrl,
                checkin_date: checkin,
                checkout_date: checkout,
                total_price: totalPrice,
                original_price: totalPrice
            };
            
            fetch('/bookings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(bookingData)
            })
            .then(res => res.json())
            .then(resData => {
                if (resData.status === 'success') {
                    alert("Đặt phòng thành công! Cảm ơn quý khách.");
                    window.location.href = "/profile";
                } else {
                    alert("Đặt phòng thất bại: " + resData.detail);
                }
            })
            .catch(err => {
                alert("Đặt phòng xảy ra lỗi: " + err);
            });
        }
        </script>
        """
        parts = html.rsplit("</body>", 1)
        if len(parts) == 2:
            html = parts[0] + detail_js + "\n" + shared_search_widget_js + "\n</body>" + parts[1]
        else:
            html += detail_js + "\n" + shared_search_widget_js

    elif t["type"] == "profile":
        # Customer bookings portal rendering
        profile_js = """
        <script>
        document.addEventListener('DOMContentLoaded', () => {
            const currentUserId = <%= user.id if user else 'null' %>;
            if (!currentUserId) {
                window.location.href = "/login?next=/profile";
                return;
            }
            const idVal = currentUserId;

            // Set user email and name on screen
            fetch(`/api/user/${idVal}`)
            .then(res => res.json())
            .then(user => {
                const nameNode = document.querySelector('[data-element-name="profile-username"]') || document.body;
                // Append simple user details section
                const infoSection = document.createElement('div');
                infoSection.style.cssText = "max-width:800px; margin:20px auto; padding:20px; background:white; border:1px solid #ddd; border-radius:8px; text-align:left;";
                infoSection.innerHTML = `
                    <h2 style="color:#1a3063; font-weight:bold; font-size:20px; margin-top:0;">Hồ sơ của bạn</h2>
                    <p style="font-size:14px; margin:5px 0;"><strong>Họ và tên:</strong> ${user.full_name}</p>
                    <p style="font-size:14px; margin:5px 0;"><strong>Email:</strong> ${user.email}</p>
                    <p style="font-size:14px; margin:5px 0;"><strong>Hạng thành viên:</strong> <span style="color:#e57237; font-weight:bold;">${user.vip_status}</span></p>
                    <p style="font-size:14px; margin:5px 0;"><strong>Điểm tích lũy:</strong> ${user.vip_points} điểm</p>
                `;
                const root = document.getElementById('home-react-root') || document.body;
                root.insertBefore(infoSection, root.firstChild);
            });

            // Retrieve bookings
            fetch(`/bookings/${idVal}`)
            .then(res => res.json())
            .then(bookings => {
                const bookingsSection = document.createElement('div');
                bookingsSection.style.cssText = "max-width:800px; margin:20px auto; padding:20px; background:white; border:1px solid #ddd; border-radius:8px; text-align:left;";
                bookingsSection.innerHTML = '<h2 style="color:#1a3063; font-weight:bold; font-size:20px; margin-top:0; margin-bottom:15px;">Lịch sử đặt phòng</h2>';
                
                if (!bookings || bookings.length === 0) {
                    bookingsSection.innerHTML += '<p style="color:#666; font-size:14px;">Bạn chưa có giao dịch đặt phòng nào.</p>';
                } else {
                    bookings.forEach(b => {
                        const statusColor = b.status === 'confirmed' ? '#00aa6c' : '#e22b35';
                        const statusLabel = b.status === 'confirmed' ? 'Thành công' : 'Đã hủy';
                        const div = document.createElement('div');
                        div.style.cssText = "border-bottom:1px solid #eee; padding:15px 0; display:flex; gap:15px;";
                        div.innerHTML = `
                            <img src="${b.property_image || 'https://images.unsplash.com/photo-1566073771259-6a8506099945'}" style="width:100px; height:80px; object-fit:cover; border-radius:4px;" />
                            <div style="flex:1;">
                                <h4 style="font-weight:bold; color:#1a3063; margin:0 0 5px 0; font-size:15px;">${b.property_name}</h4>
                                <div style="font-size:12px; color:#666; margin-bottom:3px;">📅 Thời gian: ${b.checkin_date} đến ${b.checkout_date}</div>
                                <div style="font-size:13px; font-weight:bold; color:#e57237;">Tổng giá trị: ${b.total_price.toLocaleString('vi-VN')} ₫</div>
                            </div>
                            <div style="text-align:right;">
                                <span style="background:${statusColor}; color:white; font-size:11px; font-weight:bold; padding:3px 8px; border-radius:12px;">${statusLabel}</span>
                                <div style="font-size:10px; color:#888; margin-top:8px;">Đặt ngày: ${b.created_at}</div>
                            </div>
                        `;
                        bookingsSection.appendChild(div);
                    });
                }
                const root = document.getElementById('home-react-root') || document.body;
                root.appendChild(bookingsSection);
            });
        });
        </script>
        """
        html = html.replace("</body>", profile_js + "\n</body>")

    elif t["type"] == "list_property":
        # Host Landing page
        # Replace the register button redirect link to /list-property/register
        html = re.sub(
            r'href="[^"]*register[^"]*"',
            'href="/list-property/register"',
            html,
            flags=re.IGNORECASE
        )
        # Add quick custom fallback redirect for register links
        html = html.replace('data-element-name="header-list-your-place-button"', 'onclick="window.location.href=\'/list-property/register\'"')

    elif t["type"] == "ycs_portal":
        # Host property list portal
        # Replace the header actions with YCS menu
        html = replace_html_block(html, '<div class="Box-sc-kv6pi1-0 flviCy" bis_skin_checked="1">', JINJA_YCS_HEADER)
        
        # Inject dynamic Jinja variables into property listing table
        # Let's write a simple layout override to list host's properties
        ycs_portal_js = """
        <script>
        document.addEventListener('DOMContentLoaded', () => {
            const userId = document.cookie.split('; ').find(row => row.startsWith('user_id='));
            if (!userId) {
                window.location.href = "/login?next=/ycs";
                return;
            }
            
            // Build simple clean property table in YCS portal
            const portalContainer = document.createElement('div');
            portalContainer.style.cssText = "max-width:1200px; margin:40px auto; padding:20px; background:white; border:1px solid #ddd; border-radius:8px; text-align:left;";
            portalContainer.innerHTML = `
                <div style="display:flex; justify-content:between; align-items:center; margin-bottom:20px; border-bottom:2px solid #1a3063; padding-bottom:12px; flex-direction:row;">
                    <h2 style="color:#1a3063; font-weight:bold; font-size:22px; margin:0; flex:1;">Quản lý cơ sở lưu trú của bạn</h2>
                    <a href="/list-property/register" style="background:#00aa6c; color:white; font-weight:bold; border:none; padding:10px 18px; border-radius:4px; font-size:13px; text-decoration:none; cursor:pointer; box-shadow:0 2px 4px rgba(0,170,108,0.25);">+ Đăng ký chỗ nghỉ mới</a>
                </div>
                <table style="width:100%; border-collapse:collapse; margin-top:10px;">
                    <thead>
                        <tr style="background:#f5f5f5; border-bottom:2px solid #ddd; text-align:left; font-size:13px; font-weight:bold; color:#333;">
                            <th style="padding:10px 16px;">Ảnh</th>
                            <th style="padding:10px 16px;">Tên chỗ nghỉ</th>
                            <th style="padding:10px 16px;">Mã số</th>
                            <th style="padding:10px 16px;">Thành phố</th>
                            <th style="padding:10px 16px;">Giá mỗi đêm</th>
                            <th style="padding:10px 16px;">Trạng thái</th>
                            <th style="padding:10px 16px; text-align:right;">Thao tác</th>
                        </tr>
                    </thead>
                    <tbody id="ycs-properties-table">
                        <tr><td colspan="7" style="padding:20px; text-align:center; color:#888;">Đang tải danh sách...</td></tr>
                    </tbody>
                </table>
            `;
            
            const root = document.getElementById('app-root') || document.getElementById('home-react-root') || document.body;
            root.insertBefore(portalContainer, root.firstChild);

            fetch('/api/host/properties')
            .then(res => res.json())
            .then(properties => {
                const tbody = document.getElementById('ycs-properties-table');
                tbody.innerHTML = '';
                if (!properties || properties.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="7" style="padding:30px; text-align:center; color:#666; font-size:14px;">Bạn chưa đăng ký chỗ nghỉ nào. Nhấp vào nút ở trên để bắt đầu!</td></tr>';
                    return;
                }

                properties.forEach(p => {
                    const tr = document.createElement('tr');
                    tr.style.cssText = "border-bottom:1px solid #eee; font-size:13px;";
                    tr.innerHTML = `
                        <td style="padding:12px 16px;"><img src="${p.image_url.split(',')[0]}" style="width:70px; height:50px; object-fit:cover; border-radius:4px;" /></td>
                        <td style="padding:12px 16px; font-weight:bold; color:#1a3063;">${p.name}</td>
                        <td style="padding:12px 16px; color:#666; font-family:monospace;">${p.id}</td>
                        <td style="padding:12px 16px;">${p.city}</td>
                        <td style="padding:12px 16px; font-weight:bold; color:#e57237;">${p.price.toLocaleString('vi-VN')} ₫</td>
                        <td style="padding:12px 16px;"><span style="background:#e6f4ea; color:#137333; font-weight:bold; padding:2px 8px; border-radius:12px; font-size:11px;">Hoạt động</span></td>
                        <td style="padding:12px 16px; text-align:right;">
                            <a href="/ycs/property/${p.id}" style="background:#1a3063; color:white; font-weight:bold; border:none; padding:6px 12px; border-radius:4px; font-size:11px; text-decoration:none; cursor:pointer;">Dashboard</a>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            });
        });
        </script>
        """
        html = html.replace("</body>", ycs_portal_js + "\n</body>")

    elif t["type"] == "ycs_dashboard":
        # Property management dashboard
        html = replace_html_block(html, '<div class="Box-sc-kv6pi1-0 flviCy" bis_skin_checked="1">', JINJA_YCS_HEADER)
        
        # Inject YCS Property Dashboard code (with Chart.js and statistics)
        ycs_dashboard_js = """
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
        document.addEventListener('DOMContentLoaded', () => {
            const propertyId = "<%= property.id %>";
            
            // Build clean visual dashboard overlay
            const dashboardContainer = document.createElement('div');
            dashboardContainer.style.cssText = "max-width:1200px; margin:30px auto; padding:20px; background:white; border:1px solid #ddd; border-radius:8px; text-align:left;";
            dashboardContainer.innerHTML = `
                <div style="display:flex; justify-content:between; align-items:center; margin-bottom:25px; border-bottom:2px solid #1a3063; padding-bottom:12px; flex-direction:row;">
                    <div>
                        <h2 style="color:#1a3063; font-weight:bold; font-size:22px; margin:0;">Dashboard: <%= property.name %></h2>
                        <p style="font-size:12px; color:#666; margin:4px 0 0 0;">Mã cơ sở: <span style="font-family:monospace;">${propertyId}</span> | 📍 <%= property.address %>, <%= property.city %></p>
                    </div>
                    <div style="flex:1; text-align:right;">
                        <a href="/ycs" style="background:#888; color:white; font-weight:bold; border:none; padding:8px 15px; border-radius:4px; font-size:12px; text-decoration:none; margin-right:8px;">← Trở về danh sách</a>
                        <select id="prop-select" style="padding:8px 12px; border-radius:4px; border:1px solid #ccc; font-weight:bold; font-size:12px;">
                            <% for p in all_properties %>
                                <option value="<%= p.id %>" <% if p.id == property.id %>selected<% endif %>><%= p.name %></option>
                            <% endfor %>
                        </select>
                    </div>
                </div>
                
                <!-- KPIs Row -->
                <div style="display:flex; gap:20px; margin-bottom:25px;">
                    <div style="flex:1; background:#f0f7ff; border:1px solid #c2e0ff; border-radius:8px; padding:20px; box-shadow:0 2px 4px rgba(0,0,0,0.02);">
                        <div style="font-size:12px; color:#0052cc; font-weight:bold; text-transform:uppercase;">Doanh thu tháng này (MTD)</div>
                        <div id="kpi-revenue" style="font-size:26px; font-weight:bold; color:#1a3063; margin-top:8px;">0 ₫</div>
                    </div>
                    <div style="flex:1; background:#fcf3eb; border:1px solid #ffd8b8; border-radius:8px; padding:20px; box-shadow:0 2px 4px rgba(0,0,0,0.02);">
                        <div style="font-size:12px; color:#b25900; font-weight:bold; text-transform:uppercase;">Số lượng đặt phòng</div>
                        <div id="kpi-bookings" style="font-size:26px; font-weight:bold; color:#b25900; margin-top:8px;">0 lượt</div>
                    </div>
                    <div style="flex:1; background:#e8fdf5; border:1px solid #a8f5d0; border-radius:8px; padding:20px; box-shadow:0 2px 4px rgba(0,0,0,0.02);">
                        <div style="font-size:12px; color:#137333; font-weight:bold; text-transform:uppercase;">Tỉ lệ lấp đầy phòng</div>
                        <div id="kpi-occupancy" style="font-size:26px; font-weight:bold; color:#137333; margin-top:8px;">0%</div>
                    </div>
                </div>

                <!-- Charts & Bookings Split -->
                <div style="display:flex; gap:25px; flex-direction:row;">
                    <div style="flex:1.2; background:white; border:1px solid #ddd; border-radius:8px; padding:20px;">
                        <h3 style="color:#1a3063; font-weight:bold; font-size:15px; margin-top:0; margin-bottom:15px;">Biểu đồ Doanh thu (6 tháng gần đây)</h3>
                        <canvas id="revenue-chart" style="width:100%; height:250px;"></canvas>
                    </div>
                    <div style="flex:1; background:white; border:1px solid #ddd; border-radius:8px; padding:20px; display:flex; flex-direction:column;">
                        <h3 style="color:#1a3063; font-weight:bold; font-size:15px; margin-top:0; margin-bottom:15px;">Đơn đặt phòng gần đây</h3>
                        <div id="dashboard-bookings-list" style="flex:1; overflow-y:auto; max-height:250px; font-size:12px;">
                            <div style="text-align:center; color:#888; padding:20px;">Đang tải đơn đặt...</div>
                        </div>
                    </div>
                </div>
            `;
            
            const root = document.getElementById('app-root') || document.getElementById('home-react-root') || document.body;
            root.insertBefore(dashboardContainer, root.firstChild);

            // Select redirection dropdown
            const selector = document.getElementById('prop-select');
            if (selector) {
                selector.addEventListener('change', (e) => {
                    window.location.href = `/ycs/property/${e.target.value}`;
                });
            }

            // Load analytics data
            fetch(`/api/host/properties/${propertyId}/analytics`)
            .then(res => res.json())
            .then(analytics => {
                document.getElementById('kpi-revenue').innerText = analytics.mtd_revenue.toLocaleString('vi-VN') + " ₫";
                document.getElementById('kpi-bookings').innerText = analytics.total_bookings + " lượt";
                document.getElementById('kpi-occupancy').innerText = analytics.occupancy_rate.toFixed(0) + "%";

                // Initialize Chart.js
                const ctx = document.getElementById('revenue-chart').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: analytics.chart.labels,
                        datasets: [{
                            label: 'Doanh số (VND)',
                            data: analytics.chart.data,
                            backgroundColor: '#5392f9',
                            borderColor: '#1a3063',
                            borderWidth: 1,
                            borderRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            });

            // Load bookings list
            fetch(`/api/host/properties/${propertyId}/bookings`)
            .then(res => res.json())
            .then(bookings => {
                const container = document.getElementById('dashboard-bookings-list');
                container.innerHTML = '';
                if (!bookings || bookings.length === 0) {
                    container.innerHTML = '<div style="text-align:center; color:#888; padding:20px;">Chưa có đơn đặt phòng nào.</div>';
                    return;
                }

                bookings.forEach(b => {
                    const statusColor = b.status === 'confirmed' ? '#00aa6c' : '#e22b35';
                    const div = document.createElement('div');
                    div.style.cssText = "border-bottom:1px solid #eee; padding:8px 0; display:flex; justify-content:between; align-items:center; flex-direction:row;";
                    div.innerHTML = `
                        <div style="flex:1;">
                            <div style="font-weight:bold; color:#1a3063;">${b.user_name}</div>
                            <div style="font-size:11px; color:#666;">📅 ${b.checkin_date} tới ${b.checkout_date}</div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-weight:bold; color:#e57237;">${b.total_price.toLocaleString('vi-VN')} ₫</div>
                            <span style="color:${statusColor}; font-weight:bold; font-size:10px;">${b.status === 'confirmed' ? 'Thành công' : 'Đã hủy'}</span>
                        </div>
                    `;
                    container.appendChild(div);
                });
            });
        });
        </script>
        """
        html = html.replace("</body>", ycs_dashboard_js + "\n</body>")

    elif t["type"] == "booking_detail":
        # Inject dynamic Jinja logic to render booking details from DB
        booking_detail_js = """
        <script>
        document.addEventListener('DOMContentLoaded', () => {
            const bookingId = "<%= booking.id %>";
            const propertyName = "<%= booking.property_name %>";
            const checkin = "<%= booking.checkin_date %>";
            const checkout = "<%= booking.checkout_date %>";
            const total = <%= booking.total_price %>;
            const status = "<%= booking.status %>";
            const imageUrl = "<%= booking.property_image %>";
            
            // Tìm và ghi đè nội dung receipt động
            const receiptTitle = document.querySelector('[data-element-name="receipt-property-name"]') || document.querySelector('h1') || document.querySelector('h2');
            if (receiptTitle) receiptTitle.innerText = propertyName;
            
            // Xóa nội dung thừa và chèn thông tin Booking ngắn gọn
            const mainRoot = document.getElementById('home-react-root') || document.querySelector('.Container') || document.body;
            const detailBox = document.createElement('div');
            detailBox.style.cssText = "max-width:800px; margin:20px auto; padding:20px; background:white; border:1px solid #ddd; border-radius:8px;";
            detailBox.innerHTML = `
                <h2 style="color:#1a3063; font-weight:bold; margin-bottom:15px; border-bottom:1px solid #eee; padding-bottom:10px;">Chi tiết đặt phòng #${bookingId}</h2>
                <div style="display:flex; gap:20px;">
                    <img src="${imageUrl}" style="width:200px; height:150px; object-fit:cover; border-radius:6px;" />
                    <div>
                        <h3 style="margin:0 0 10px 0; color:#1a3063;">${propertyName}</h3>
                        <p><strong>Ngày nhận phòng:</strong> ${checkin}</p>
                        <p><strong>Ngày trả phòng:</strong> ${checkout}</p>
                        <p><strong>Trạng thái:</strong> <span style="background:${status==='confirmed'?'#00aa6c':'#e22b35'}; color:white; padding:4px 8px; border-radius:4px; font-weight:bold;">${status==='confirmed'?'Đã xác nhận':'Đã hủy'}</span></p>
                        <p><strong>Tổng tiền:</strong> <span style="color:#e57237; font-size:20px; font-weight:bold;">${total.toLocaleString('vi-VN')} ₫</span></p>
                    </div>
                </div>
            `;
            mainRoot.insertBefore(detailBox, mainRoot.firstChild);
        });
        </script>
        """
        parts = html.rsplit("</body>", 1)
        if len(parts) == 2:
            html = parts[0] + booking_detail_js + "\n</body>" + parts[1]
        else:
            html += booking_detail_js

    elif t["type"] in ["trips", "bookings_list"]:
        # Tương tự như profile, nhưng render danh sách booking
        trips_js = """
        <script>
        document.addEventListener('DOMContentLoaded', () => {
            const currentUserId = <%= user.id if user else 'null' %>;
            if (!currentUserId) {
                window.location.href = "/login?next=/trips";
                return;
            }
            const idVal = currentUserId;

            fetch(`/bookings/${idVal}`)
            .then(res => res.json())
            .then(bookings => {
                const bookingsSection = document.createElement('div');
                bookingsSection.style.cssText = "max-width:900px; margin:20px auto; padding:20px; background:white; border:1px solid #ddd; border-radius:8px; text-align:left;";
                bookingsSection.innerHTML = '<h2 style="color:#1a3063; font-weight:bold; font-size:22px; margin-top:0; margin-bottom:15px;">Chuyến đi của bạn</h2>';
                
                if (!bookings || bookings.length === 0) {
                    bookingsSection.innerHTML += '<p style="color:#666; font-size:15px; padding:20px; text-align:center;">Bạn chưa có chuyến đi nào sắp tới.</p>';
                } else {
                    bookings.forEach(b => {
                        const statusColor = b.status === 'confirmed' ? '#00aa6c' : '#e22b35';
                        const statusLabel = b.status === 'confirmed' ? 'Đã xác nhận' : 'Đã hủy';
                        const div = document.createElement('div');
                        div.style.cssText = "border:1px solid #e1e8ed; margin-bottom:15px; border-radius:8px; display:flex; overflow:hidden; box-shadow:0 2px 4px rgba(0,0,0,0.05);";
                        div.innerHTML = `
                            <img src="${b.property_image || 'https://images.unsplash.com/photo-1566073771259-6a8506099945'}" style="width:220px; height:150px; object-fit:cover;" />
                            <div style="padding:15px; flex:1; display:flex; flex-direction:column; justify-content:space-between;">
                                <div>
                                    <h4 style="font-weight:bold; color:#1a3063; margin:0 0 5px 0; font-size:18px;">${b.property_name}</h4>
                                    <div style="font-size:13px; color:#666; margin-bottom:10px;">📅 Nhận phòng: <strong>${b.checkin_date}</strong> - Trả phòng: <strong>${b.checkout_date}</strong></div>
                                </div>
                                <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                                    <span style="background:${statusColor}; color:white; font-size:12px; font-weight:bold; padding:4px 10px; border-radius:12px;">${statusLabel}</span>
                                    <div style="text-align:right;">
                                        <div style="font-size:12px; color:#888;">Tổng giá trị</div>
                                        <div style="font-size:18px; font-weight:bold; color:#e57237;">${b.total_price.toLocaleString('vi-VN')} ₫</div>
                                    </div>
                                </div>
                            </div>
                            <div style="width:140px; border-left:1px solid #e1e8ed; display:flex; flex-direction:column; justify-content:center; align-items:center; padding:15px; background:#f9f9f9;">
                                <a href="/booking/${b.id}" style="background:#5392f9; color:white; font-weight:bold; font-size:12px; padding:8px 15px; border-radius:4px; text-decoration:none; text-align:center; display:block; width:100%; margin-bottom:10px;">Chi tiết</a>
                                <a href="/reviews/submit/${b.id}" style="background:transparent; color:#5392f9; border:1px solid #5392f9; font-weight:bold; font-size:12px; padding:8px 15px; border-radius:4px; text-decoration:none; text-align:center; display:block; width:100%;">Viết nhận xét</a>
                            </div>
                        `;
                        bookingsSection.appendChild(div);
                    });
                }
                const root = document.getElementById('home-react-root') || document.querySelector('.Container') || document.body;
                root.insertBefore(bookingsSection, root.firstChild);
            });
        });
        </script>
        """
        parts = html.rsplit("</body>", 1)
        if len(parts) == 2:
            html = parts[0] + trips_js + "\n</body>" + parts[1]
        else:
            html += trips_js

    elif t["type"] == "agodacash":
        js = """
        <script>
        document.addEventListener('DOMContentLoaded', () => {
            fetch('/api/user/agodacash').then(res => res.json()).then(data => {
                const balEl = document.querySelector('[data-element-name="agodacash-balance-text"]') || document.querySelector('h1') || document.body;
                if(balEl && balEl.innerText.includes('AgodaCash')) {
                    balEl.innerText = 'Số dư: ' + data.balance.toLocaleString('vi-VN') + ' ₫';
                }
                document.querySelectorAll('span').forEach(span => {
                    if(span.innerText === '0 ₫') span.innerText = data.balance.toLocaleString('vi-VN') + ' ₫';
                });
            });
        });
        </script>
        """
        html = html.replace("</body>", js + "\n</body>")

    elif t["type"] == "vip":
        js = """
        <script>
        document.addEventListener('DOMContentLoaded', () => {
            fetch('/api/user/vip').then(res => res.json()).then(data => {
                const tierEls = document.querySelectorAll('span, h2, h3, p');
                tierEls.forEach(el => {
                    if (el.innerText.includes('Đồng') || el.innerText.includes('Bronze')) {
                        el.innerText = el.innerText.replace(/Đồng|Bronze/g, data.tier);
                    }
                });
            });
        });
        </script>
        """
        html = html.replace("</body>", js + "\n</body>")

    elif t["type"] == "inbox":
        js = """
        <script>
        document.addEventListener('DOMContentLoaded', () => {
            fetch('/api/user/inbox').catch(()=>fetch('/api/inbox')).then(res => res.json()).then(messages => {
                let container = document.querySelector('[data-element-name="inbox-list-container"]') || document.querySelector('.Box-sc-kv6pi1-0.hXzSTv') || document.querySelector('main');
                if(!container) return;
                
                if (messages.length === 0) {
                    container.innerHTML = '<div style="padding:40px; text-align:center; color:#666;">Không có tin nhắn nào.</div>';
                    return;
                }
                
                let html = '<div style="max-width:800px; margin:20px auto; background:white; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.1);">';
                messages.forEach(m => {
                    const fw = m.is_read ? 'normal' : 'bold';
                    const bg = m.is_read ? '#fff' : '#f4f8ff';
                    html += `
                        <div style="padding:15px 20px; border-bottom:1px solid #eee; background:${bg}; cursor:pointer;" onclick="markRead(${m.id}, this)">
                            <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                                <span style="font-weight:${fw}; color:#1a3063;">${m.sender}</span>
                                <span style="font-size:12px; color:#888;">${m.date}</span>
                            </div>
                            <div style="font-weight:${fw}; font-size:15px; margin-bottom:5px;">${m.subject}</div>
                            <div style="color:#666; font-size:13px; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;">${m.content}</div>
                        </div>
                    `;
                });
                html += '</div>';
                
                container.innerHTML = html;
            });
        });
        function markRead(id, el) {
            fetch(`/api/inbox/mark_read/${id}`, {method: 'POST'});
            el.style.background = '#fff';
            el.style.fontWeight = 'normal';
        }
        </script>
        """
        html = html.replace("</body>", js + "\n</body>")

    elif t["type"] == "reviews":
        js = """
        <script>
        document.addEventListener('DOMContentLoaded', () => {
            fetch('/api/reviews').then(res => res.json()).then(reviews => {
                let container = document.querySelector('[data-element-name="reviews-list"]') || document.querySelector('main');
                if(!container) return;
                
                if (reviews.length === 0) {
                    container.innerHTML = '<div style="padding:40px; text-align:center; color:#666;">Bạn chưa viết đánh giá nào.</div>';
                    return;
                }
                
                let html = '<div style="max-width:800px; margin:20px auto;">';
                reviews.forEach(r => {
                    const stars = '★'.repeat(Math.round(r.rating));
                    html += `
                        <div style="padding:20px; border:1px solid #ddd; border-radius:8px; margin-bottom:15px; background:white;">
                            <h3 style="margin:0 0 10px 0; color:#1a3063;">${r.property_name}</h3>
                            <div style="color:#ffaa00; font-size:18px; margin-bottom:10px;">${stars}</div>
                            <div style="color:#333; line-height:1.5;">${r.comment}</div>
                            <div style="color:#999; font-size:12px; margin-top:10px;">Đã đăng vào ${r.date}</div>
                        </div>
                    `;
                });
                html += '</div>';
                container.innerHTML = html;
            });
        });
        </script>
        """
        html = html.replace("</body>", js + "\n</body>")

    elif t["type"] == "submit_review":
        js = """
        <script>
        document.addEventListener('DOMContentLoaded', () => {
            const formHtml = `
            <div style="max-width:600px; margin:40px auto; background:white; padding:30px; border-radius:8px; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
                <h2 style="color:#1a3063; margin-bottom:20px;">Viết Đánh Giá</h2>
                <div style="margin-bottom:20px;">
                    <label style="display:block; font-weight:bold; margin-bottom:8px;">Điểm đánh giá (1-5)</label>
                    <input type="number" id="review-rating" min="1" max="5" value="5" style="width:100%; padding:10px; border:1px solid #ddd; border-radius:4px;">
                </div>
                <div style="margin-bottom:20px;">
                    <label style="display:block; font-weight:bold; margin-bottom:8px;">Nhận xét của bạn</label>
                    <textarea id="review-comment" rows="5" style="width:100%; padding:10px; border:1px solid #ddd; border-radius:4px;" placeholder="Chia sẻ trải nghiệm của bạn..."></textarea>
                </div>
                <button id="submit-review-btn" style="background:#5392f9; color:white; border:none; padding:12px 24px; font-weight:bold; border-radius:4px; cursor:pointer; width:100%;">Gửi đánh giá & Nhận 10.000 ₫</button>
            </div>
            `;
            
            const mainRoot = document.querySelector('main') || document.body;
            mainRoot.innerHTML = formHtml;
            
            document.getElementById('submit-review-btn').addEventListener('click', () => {
                const rating = document.getElementById('review-rating').value;
                const comment = document.getElementById('review-comment').value;
                
                const urlPath = window.location.pathname;
                const bookingId = urlPath.split('/').pop() || 1;
                
                fetch('/api/reviews', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        booking_id: parseInt(bookingId),
                        property_name: "Khách sạn (Từ Đơn hàng #" + bookingId + ")",
                        rating: parseFloat(rating),
                        comment: comment
                    })
                }).then(res => res.json()).then(data => {
                    if (data.status === 'success') {
                        alert("Cảm ơn bạn! Đánh giá đã được ghi nhận. Bạn nhận được " + data.reward + " ₫ AgodaCash.");
                        window.location.href = '/reviews';
                    } else {
                        alert("Lỗi: " + data.detail);
                    }
                });
            });
        });
        </script>
        """
        html = html.replace("</body>", js + "\n</body>")

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"Successfully processed {t['dest_file']}")

if __name__ == "__main__":
    print("=== START CLEANING AND SYNCHRONIZING AGODA TEMPLATES ===")
    for mapping in TEMPLATES_MAPPING:
        try:
            clean_template_file(mapping)
        except Exception as e:
            print(f"ERROR processing {mapping['dest_file']}: {e}")
    print("=== SYNCHRONIZATION COMPLETE ===")
