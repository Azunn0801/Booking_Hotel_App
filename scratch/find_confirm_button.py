import re

with open('scratch/bookings_list_button_output.txt', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('ĐẶT NGAY!')
with open('scratch/find_confirm_button_output.txt', 'w', encoding='utf-8') as out:
    if pos != -1:
        out.write("FOUND:\n")
        out.write(text[pos - 800:pos + 200])
    else:
        out.write("NOT FOUND\n")
print("Done")
