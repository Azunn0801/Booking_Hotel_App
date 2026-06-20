with open('web_platform/templates/bookings_list.html', 'r', encoding='utf-8') as f:
    content = f.read()

pos = 1542185
start = max(0, pos - 1500)
end = min(len(content), pos + 1500)

with open('scratch/bookings_list_button_output.txt', 'w', encoding='utf-8') as out:
    out.write(content[start:end])

print("Written surrounding text of button to scratch/bookings_list_button_output.txt")
