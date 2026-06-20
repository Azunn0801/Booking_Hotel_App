from bs4 import BeautifulSoup

html = open('d:/4Study/PTIT/Year 2/Semester 2/Phat trien huong dich vu/Hotel App/web_platform/templates/search.html', encoding='utf-8').read()
soup = BeautifulSoup(html, 'html.parser')

card = soup.find('li', class_='PropertyCardItem')
if card:
    seleniums = card.find_all(attrs={"data-selenium": True})
    for tag in seleniums:
        print(f"data-selenium='{tag['data-selenium']}' -> text='{tag.text.strip()}' class='{tag.get('class')}'")
        
    imgs = card.find_all('img')
    print("Images:", [img.get('src') for img in imgs])
else:
    print("Not found")
