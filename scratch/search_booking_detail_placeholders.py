import re

with open('web_platform/templates/booking_detail.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for:
# - property-card-name
# - jnozbv
# - 1738373829
# - 24 thg 6 2026 or 25 thg 6 2026
# - Nguyen Dung or Dung Nguyen
# - payment-card-price-item-final-amount

keywords = [
    'property-card-name',
    '1738373829',
    '24 thg 6 2026',
    '25 thg 6 2026',
    'Nguyen Dung',
    'payment-card-price-item-final-amount'
]

with open('scratch/booking_detail_placeholders.json', 'w', encoding='utf-8') as out:
    out.write("Searching in booking_detail.html:\n")
    for kw in keywords:
        pos = content.find(kw)
        if pos != -1:
            snippet = content[max(0, pos - 80):min(len(content), pos + 120)].replace('\n', ' ')
            out.write(f"Keyword: {kw} -> {snippet}\n")
        else:
            out.write(f"Keyword: {kw} -> NOT FOUND\n")

print("Done writing findings to scratch/booking_detail_placeholders.json")
