import re

with open('web_platform/templates/bookings_list.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for the IDs or elements of interest:
# contact.contactFirstName, contact.contactLastName, contact.contactEmail, contact.contactPhoneNumber, property.address1
ids_to_find = [
    'contact.contactFirstName',
    'contact.contactLastName',
    'contact.contactEmail',
    'contact.contactPhoneNumber',
    'property.address1'
]

with open('scratch/bookings_list_texts.json', 'w', encoding='utf-8') as out:
    out.write("Searching in bookings_list.html:\n")
    for i in ids_to_find:
        pos = content.find(f'id="{i}"')
        if pos == -1:
            pos = content.find(f"id='{i}'")
        if pos != -1:
            snippet = content[max(0, pos - 50):min(len(content), pos + 150)].replace('\n', ' ')
            out.write(f"ID: {i} -> {snippet}\n")
        else:
            out.write(f"ID: {i} -> NOT FOUND\n")

    # Let's search for property-name-id or total-price or room-price
    for attr in ['property-name-id', 'fpc-room-price', 'fpc-tax-and-fee-amount', 'fpc-total-price']:
        pos = content.find(attr)
        if pos != -1:
            snippet = content[max(0, pos - 50):min(len(content), pos + 150)].replace('\n', ' ')
            out.write(f"Attr: {attr} -> {snippet}\n")
        else:
            out.write(f"Attr: {attr} -> NOT FOUND\n")

print("Done writing findings to scratch/bookings_list_texts.json")
