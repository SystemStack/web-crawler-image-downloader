"""A simple web crawler -- class implementing crawling logic."""

import asyncio
import cgi
from collections import namedtuple
import re
import time
import urllib.parse
import urllib.robotparser
from htmlParse import MyHTMLParser
from tablePrint import Table_Print
try:
    # Python 3.4.
    from asyncio import JoinableQueue as Queue
except ImportError:
    # Python 3.5.
    from asyncio import Queue

import aiohttp  # Install with "pip install aiohttp".

def lenient_host(host):
    parts = host.split('.')[-2:]
    return ''.join(parts)

def is_redirect(response):
    return response.status in (300, 301, 302, 303, 307)

FetchStatistic = namedtuple('FetchStatistic',
                            ['url',
                             'next_url',
                             'status',
                             'exception',
                             'size',
                             'content_type',
                             'encoding',
                             'num_urls',
                             'num_new_urls'])


class Crawler:
    """Crawl a set of URLs.

    This manages two sets of URLs: 'urls' and 'done'.  'urls' is a set of
    URLs seen, and 'done' is a list of FetchStatistics.
    """
    robots=[]
    def __init__(self, roots,
                 exclude=None, strict=True,  # What to crawl.
                 max_redirect=10, max_tries=4,  # Per-url limits.
                 max_tasks=10, *, loop=None,
                 robots_txt=[], download_images=False,
                 table=None):
        self.loop = loop or asyncio.get_event_loop()
        self.roots = roots
        self.exclude = exclude
        self.strict = strict
        self.max_redirect = max_redirect
        self.max_tries = max_tries
        self.max_tasks = max_tasks
        self.q = Queue(loop=self.loop)
        self.seen_urls = set()
        self.done = []
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.root_domains = set()
        self.robots_txt = robots_txt
        self.table = table
        self.download_images = download_images

        for url in robots_txt:
            rp = urllib.robotparser.RobotFileParser(url)
            rp.set_url(url)
            self.robots.append(rp)

        if self.download_images:
            self.HTML_parser = MyHTMLParser()

            root_url = roots.pop()
            roots.add(root_url + "/")
            self.HTML_parser.root_url = root_url

        for root in roots:
            parts = urllib.parse.urlparse(root)
            host, port = urllib.parse.splitport(parts.netloc)
            if not host:
                continue
            if re.match(r'\A[\d\.]*\Z', host):
                self.root_domains.add(host)
            else:
                host = host.lower()
                if self.strict:
                    self.root_domains.add(host)
                else:
                    self.root_domains.add(lenient_host(host))
        for root in roots:
            self.add_url(root)
        self.t1 = None

    def close(self):
        """Close resources."""
        self.session.close()

    def host_okay(self, host):
        """Check if a host should be crawled.

        A literal match (after lowercasing) is always good.  For hosts
        that don't look like IP addresses, some approximate matches
        are okay depending on the strict flag.
        """
        host = host.lower()
        if host in self.root_domains:
            return True
        if re.match(r'\A[\d\.]*\Z', host):
            return False
        if self.strict:
            return self._host_okay_strictish(host)
        else:
            return self._host_okay_lenient(host)

    def _host_okay_strictish(self, host):
        """Check if a host should be crawled, strict-ish version.

        This checks for equality modulo an initial 'www.' component.
        """
        host = host[4:] if host.startswith('www.') else 'www.' + host
        return host in self.root_domains

    def _host_okay_lenient(self, host):
        """Check if a host should be crawled, lenient version.

        This compares the last two components of the host.
        """
        return lenient_host(host) in self.root_domains

    def record_statistic(self, fetch_statistic):
        """Record the FetchStatistic for completed / failed URL."""
        self.done.append(fetch_statistic)

    @asyncio.coroutine
    def parse_links(self, response):
        """Return a FetchStatistic and list of links."""
        links = set()
        content_type = None
        encoding = None
        body = yield from response.read()
        if response.status == 200:
            content_type = response.headers.get('content-type')
            pdict = {}
            if content_type:
                content_type, pdict = cgi.parse_header(content_type)

            encoding = pdict.get('charset', 'utf-8')
            if content_type in ('text/html', 'application/xml'):
                text = yield from response.text()
                # If user wants to download images, this will create a set of
                # all of the images on the site
                if self.download_images:
                    self.HTML_parser.feed(text)
                urls = set(re.findall(r'''(?i)href=["']([^\s"'<>]+)''', text))
                for url in urls:
                    self.table.tabularize('URL', 'got ' + str((len(urls))) + ' distinct urls from ' + response.url)
                    normalized = urllib.parse.urljoin(response.url, url)
                    defragmented, frag = urllib.parse.urldefrag(normalized)
                    if self.url_allowed(defragmented):
                        links.add(defragmented)

        stat = FetchStatistic(
            url=response.url,
            next_url=None,
            status=response.status,
            exception=None,
            size=len(body),
            content_type=content_type,
            encoding=encoding,
            num_urls=len(links),
            num_new_urls=len(links - self.seen_urls))
        return stat, links



    @asyncio.coroutine
    def fetch(self, url, max_redirect):
        """Fetch one URL."""
        tries = 0
        exception = None
        while tries < self.max_tries:
            try:
                response = yield from self.session.get(
                    url, allow_redirects=False)
                if tries > 1:
                    self.table.tabularize('TRIES',
                                       'try {0} for {1} success'.format(tries, url))
                break
            except aiohttp.ClientError as client_error:
                self.table.tabularize('TRIES_RAISED',
                   'try {0} for {1} raise {2}'.format(tries, url, client_error))
                exception = client_error
            tries += 1
        else:
            # We never broke out of the loop: all tries failed.
            self.table.tabularize('TRIES_FAILED',
                   '{0} failed after {1} tries'.format(url, self.max_tries))
            self.record_statistic(FetchStatistic(url=url,
                                                 next_url=None,
                                                 status=None,
                                                 exception=exception,
                                                 size=0,
                                                 content_type=None,
                                                 encoding=None,
                                                 num_urls=0,
                                                 num_new_urls=0))
            return

        try:
            if is_redirect(response):
                location = response.headers['location']
                next_url = urllib.parse.urljoin(url, location)
                self.record_statistic(FetchStatistic(url=url,
                                                     next_url=next_url,
                                                     status=response.status,
                                                     exception=None,
                                                     size=0,
                                                     content_type=None,
                                                     encoding=None,
                                                     num_urls=0,
                                                     num_new_urls=0))

                if next_url in self.seen_urls:
                    return
                if max_redirect > 0:
                    self.table.tabularize('REDIRECT',
                                       'To {0} from {1}'.format(next_url, url))
                    self.add_url(next_url, max_redirect - 1)
                else:
                    self.table.tabularize('LIMITREACHED',
                                       'redirect limit reached for {0} from {1}'.format(next_url, url))
            else:
                stat, links = yield from self.parse_links(response)
                self.record_statistic(stat)
                for link in links.difference(self.seen_urls):
                    self.q.put_nowait((link, self.max_redirect))
                self.seen_urls.update(links)
        finally:
            yield from response.release()

    @asyncio.coroutine
    def work(self):
        """Process queue items forever."""
        try:
            while True:
                url, max_redirect = yield from self.q.get()
                assert url in self.seen_urls
                yield from self.fetch(url, max_redirect)
                self.q.task_done()
        except asyncio.CancelledError:
            pass

    def url_allowed(self, url):
        if self.exclude and re.search(self.exclude, url):
            return False
        parts = urllib.parse.urlparse(url)
        if parts.scheme not in ('http', 'https'):
            self.table.tabularize('SKIP_BAD_SCHEME',
                               'skipping non-http scheme in {0}'.format(url))
            return False
        host, port = urllib.parse.splitport(parts.netloc)
        if not self.host_okay(host):
            self.table.tabularize('SKIP_ROOT',
                               'skipping non-root host in {0}'.format(url))
            return False
        for e in self.robots:
            e.read()
            if not e.can_fetch("*", url):
                return False
        return True

    def add_url(self, url, max_redirect=None):
        """Add a URL to the queue if not seen before."""
        if max_redirect is None:
            max_redirect = self.max_redirect
        self.table.tabularize('SKIP_BAD_SCHEME',
                           'adding {0} {1}'.format(url, max_redirect))
        self.seen_urls.add(url)
        self.q.put_nowait((url, max_redirect))


    @asyncio.coroutine
    def crawl(self):
        """Run the crawler until all finished."""
        workers = [asyncio.Task(self.work(), loop=self.loop)
                   for _ in range(self.max_tasks)]
        self.t0 = self.table.t0
        yield from self.q.join()

        self.t1 = time.time()
        for w in workers:
            w.cancel()
