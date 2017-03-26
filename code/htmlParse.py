from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    start_attrs = []
    image_urls = set()

    def handle_starttag(self, tag, attrs):
        self.start_tag = tag
        if attrs != []:
            self.start_attrs.extend(attrs)

    def handle_endtag(self, tag):
        self.end_tag = tag

    def handle_data(self, data):
        self.data = data

    def image_helper(self, url):
        if(url[:2] == "//"):
            return url[2:]
        elif(url[:4] == "http"):
            return url
        else:
            return None

    def handle_startendtag(self, tag, attrs):
        if tag=="img":
            self.image_urls.add(self.image_helper(attrs[0][1]))

