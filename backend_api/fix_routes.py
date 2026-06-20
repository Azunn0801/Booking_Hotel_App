import os
path = 'd:/4Study/PTIT/Year 2/Semester 2/Phat trien huong dich vu/Hotel App/backend_api/app/main.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

part1, part2 = content.split('# Extended User Endpoints (AgodaCash, VIP, Inbox, Reviews)')
user_id_route = '@app.get("/api/user/{user_id}")'
p1, p2 = part1.split(user_id_route)

new_content = p1 + '# Extended User Endpoints (AgodaCash, VIP, Inbox, Reviews)' + part2 + user_id_route + p2

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Reordered successfully')
