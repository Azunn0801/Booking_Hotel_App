import re

with open('web_platform/templates/profile.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for id="..." patterns containing mmb
matches = re.findall(r'<[^>]*\bid=["\'](mmb-[^"\']+)["\'][^>]*>', content)
matches = list(set(matches))
matches.sort()

# For each match, let's pull a snippet of the tag and write to file
with open('scratch/search_profile_name_edit_output.txt', 'w', encoding='utf-8') as out:
    for m in matches:
        pos = content.find(f'id="{m}"')
        if pos == -1:
            pos = content.find(f"id='{m}'")
        if pos != -1:
            start = max(0, pos - 40)
            end = min(len(content), pos + 120)
            snippet = content[start:end].replace('\n', ' ')
            out.write(f"ID: {m} -> {snippet}\n")
print("Done writing results to scratch/search_profile_name_edit_output.txt")
