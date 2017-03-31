from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    # Set that we will use to download the images from later
    image_urls = set()

    # Handles self-closing tags like <br> <img> <input>
    def handle_startendtag(self, tag, attrs):
        if tag == "img":
            self.image_urls.add(self.image_helper(attrs[0][1]))

    def image_helper(self, url):
        # Relative path, double slash means the browser gets to select
        # between http and https
        if(url[:2] == "//"):
            return "http:" + url
        # Relatve path but defaults to http
        elif(url[:1] == "/"):
            return self.root_url + url[1:]
        # Properly formed URL
        elif(url[:4] == "http"):
            return url
        # Malformed URL, cannot be handled
        return
