import re

with open('web_platform/templates/profile.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for patterns with class or id containing "vip" or "point" or "pointsmax"
# Let's search for text content "điểm" or "VIP"
matches = re.finditer(r'<[^>]*\b(class|id)=["\'][^"\']*(vip|point|agodavip|cashback)[^"\']*["\'][^>]*>', content, re.I)

seen = set()
with open('scratch/search_profile_vip_output.txt', 'w', encoding='utf-8') as out:
    for m in matches:
        tag_str = m.group(0)
        if tag_str not in seen:
            seen.add(tag_str)
            pos = m.start()
            start = max(0, pos - 20)
            end = min(len(content), pos + 150)
            snippet = content[start:end].replace('\n', ' ')
            out.write(f"Match: {snippet}\n")
print(f"Done. Found {len(seen)} unique tag snippets.")
