from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    start_attrs = []

    def handle_starttag(self, tag, attrs):
        # print("Start Tag", tag)
        self.start_tag = tag
        if attrs != []:
            self.start_attrs.extend(attrs)

    def handle_endtag(self, tag):
        # print("End Tag", tag)
        self.end_tag = tag

    def handle_data(self, data):
        # print("Data", data)
        self.data = data

# parser.feed('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
#             '"http://www.w3.org/TR/html4/strict.dtd">')
# parser.feed('<img src="python-logo.png" alt="The Python logo">')

# parser.feed('<style type="text/css">#python { color: green }</style>')



#cls | python .\crawl.py uwosh.edu wisc.edu
