import re
html = open('d:/4Study/PTIT/Year 2/Semester 2/Phat trien huong dich vu/Hotel App/web_platform/templates/search.html', encoding='utf-8').read()
inputs = re.findall(r'<input[^>]+>', html)
for i in inputs[:20]:
    match = re.search(r'id="([^"]+)"', i)
    print(match.group(1) if match else "NO_ID", "-->", i)
