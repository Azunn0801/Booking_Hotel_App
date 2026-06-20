import re

with open('web_platform/templates/bookings_list.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for all <input> tags and see their IDs
inputs = re.findall(r'<input[^>]*>', content)
# Let's search for any button containing "ĐẶT NGAY" or "Đặt ngay" or "ĐẶT" or "đặt"
buttons = re.findall(r'<button[^>]*>.*?</button>', content, re.I)

# Also let's search for text "ĐẶT NGAY"
text_pos = [m.start() for m in re.finditer(r'ĐẶT NGAY', content)]

with open('scratch/search_bookings_list_confirm_output.txt', 'w', encoding='utf-8') as out:
    out.write("INPUT TAGS:\n")
    for ip in inputs:
        if 'contact' in ip or 'property' in ip or 'first' in ip or 'last' in ip or 'email' in ip or 'phone' in ip:
            out.write(f"  {ip}\n")
            
    out.write("\nBUTTON TAGS:\n")
    for btn in buttons:
        if 'ĐẶT' in btn or 'DAT' in btn or 'xác nhận' in btn.lower() or 'book' in btn.lower():
            out.write(f"  {btn}\n")
            
    out.write("\nTEXT POSITIONS FOR 'ĐẶT NGAY':\n")
    for pos in text_pos:
        snippet = content[max(0, pos - 50):min(len(content), pos + 100)].replace('\n', ' ')
        out.write(f"  Pos {pos} -> {snippet}\n")

print("Done writing findings to scratch/search_bookings_list_confirm_output.txt")
