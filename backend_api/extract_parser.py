from html.parser import HTMLParser

class CardParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_card = False
        self.card_html = []
        self.li_depth = 0
        self.card_found = False

    def handle_starttag(self, tag, attrs):
        if self.card_found:
            return
        
        attrs_dict = dict(attrs)
        if tag == 'li' and 'PropertyCardItem' in attrs_dict.get('class', ''):
            self.in_card = True
            self.li_depth = 1
            
        if self.in_card:
            self.card_html.append(f"<{tag} " + " ".join([f'{k}="{v}"' for k,v in attrs]) + ">")
            if tag == 'li' and 'PropertyCardItem' not in attrs_dict.get('class', ''):
                self.li_depth += 1

    def handle_endtag(self, tag):
        if self.card_found:
            return
            
        if self.in_card:
            self.card_html.append(f"</{tag}>")
            if tag == 'li':
                self.li_depth -= 1
                if self.li_depth == 0:
                    self.in_card = False
                    self.card_found = True

    def handle_data(self, data):
        if self.in_card and not self.card_found:
            self.card_html.append(data)

html = open('d:/4Study/PTIT/Year 2/Semester 2/Phat trien huong dich vu/Hotel App/web_platform/templates/search.html', encoding='utf-8').read()
parser = CardParser()
parser.feed(html)
open('d:/4Study/PTIT/Year 2/Semester 2/Phat trien huong dich vu/Hotel App/backend_api/card_full.html', 'w', encoding='utf-8').write("".join(parser.card_html))
print("Extraction complete")
