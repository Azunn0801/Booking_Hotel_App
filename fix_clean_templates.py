import os

fpath = 'd:/4Study/PTIT/Year 2/Semester 2/Phat trien huong dich vu/Hotel App/tools/clean_templates.py'
with open(fpath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace detail_js injection
old_str = 'html = html.replace("</body>", detail_js + "\\n</body>")'
new_str = '''parts = html.rsplit("</body>", 1)
        if len(parts) == 2:
            html = parts[0] + detail_js + "\\n</body>" + parts[1]
        else:
            html += detail_js'''
content = content.replace(old_str, new_str)

# Replace search_results_js injection
old_str2 = 'html = html.replace("</body>", search_results_js + "\\n</body>")'
new_str2 = '''parts = html.rsplit("</body>", 1)
        if len(parts) == 2:
            html = parts[0] + search_results_js + "\\n</body>" + parts[1]
        else:
            html += search_results_js'''
content = content.replace(old_str2, new_str2)

with open(fpath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed clean_templates.py successfully.")
