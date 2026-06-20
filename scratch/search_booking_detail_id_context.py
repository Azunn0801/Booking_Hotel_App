import re

with open('web_platform/templates/booking_detail.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for img tags
imgs = re.findall(r'<img[^>]*>', content)

with open('scratch/booking_detail_ids.txt', 'w', encoding='utf-8') as out:
    out.write("IMG TAGS:\n")
    for img in imgs:
        out.write(f"  {img}\n")

print("Done")
