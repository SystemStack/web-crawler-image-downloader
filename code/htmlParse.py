from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    start_attrs = []

    def handle_starttag(self, tag, attrs):
        self.start_tag = tag
        if attrs != []:
            self.start_attrs.extend(attrs)

    def handle_endtag(self, tag):
        self.end_tag = tag

    def handle_data(self, data):
        self.data = data