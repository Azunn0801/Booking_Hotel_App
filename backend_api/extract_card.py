import re
import json

html = open('d:/4Study/PTIT/Year 2/Semester 2/Phat trien huong dich vu/Hotel App/web_platform/templates/search.html', encoding='utf-8').read()

# Find the first PropertyCardItem
card_match = re.search(r'<li[^>]*PropertyCardItem[^>]*>.*?</li>', html, re.DOTALL)
if card_match:
    card_html = card_match.group(0)
    print("Found Card HTML size:", len(card_html))
    
    # Find all data-selenium attributes inside it
    selenium_attrs = re.findall(r'data-selenium="([^"]+)"', card_html)
    print("SELENIUM ATTRS:", set(selenium_attrs))
    
    # Check if image is an img tag or background-image
    images = re.findall(r'<img[^>]+src="([^"]+)"', card_html)
    print("IMAGES:", images)
else:
    print("NO CARD FOUND")
