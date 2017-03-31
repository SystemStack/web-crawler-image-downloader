#!/usr/bin/env python3.4

"""A simple web crawler -- main driver program."""

# TODO:
# - Add arguments to specify TLS settings (e.g. cert/key files).

import argparse
import asyncio
import logging
import sys

import crawling
import reporting
from html.parser import HTMLParser
from fileDownloader import File_Downloader
from tablePrint import Table_Print
ARGS = argparse.ArgumentParser(description="Web crawler")
ARGS.add_argument(
    '--iocp', action='store_true', dest='iocp',
    default=False, help='Use IOCP event loop (Windows only)')
ARGS.add_argument(
    '--select', action='store_true', dest='select',
    default=False, help='Use Select event loop instead of default')
ARGS.add_argument(
    'roots', nargs='*',
    default=[], help='Root URL (may be repeated)')
ARGS.add_argument(
    '--max_redirect', action='store', type=int, metavar='N',
    default=10, help='Limit redirection chains (for 301, 302 etc.)')
ARGS.add_argument(
    '--max_tries', action='store', type=int, metavar='N',
    default=4, help='Limit retries on network errors')
ARGS.add_argument(
    '--max_tasks', action='store', type=int, metavar='N',
    default=100, help='Limit concurrent connections')
ARGS.add_argument(
    '--exclude', action='store', metavar='REGEX',
    help='Exclude matching URLs')
ARGS.add_argument(
    '--strict', action='store_true',
    default=True, help='Strict host matching (default)')
ARGS.add_argument(
    '--lenient', action='store_false', dest='strict',
    default=False, help='Lenient host matching')
ARGS.add_argument(
    '-v', '--verbose', action='count', dest='level',
    default=2, help='Verbose logging (repeat for more verbose)')
ARGS.add_argument(
    '-q', '--quiet', action='store_const', const=0, dest='level',
    default=2, help='Only log errors')
ARGS.add_argument(
    '--robots', nargs='*',
    default=[], help='Add a robots.txt url')
ARGS.add_argument(
    '-d', '--download', action='store_true', dest='download_images',
    default=False, help='Download all images')
ARGS.add_argument(
    '-sl', '--save_log', action='store', dest='save_log',
    default="", help='Save logs of report')


def fix_url(url):
    """Prefix a schema-less URL with http://."""
    if '://' not in url:
        url = 'http://' + url
    return url

def main():
    """Main program.

    Parse arguments, set up event loop, run crawler, print report.
    """
    args = ARGS.parse_args()
    if not args.roots:
        print('Use --help for command line help')
        return

    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
    logging.basicConfig(level=levels[min(args.level, len(levels)-1)])

    if args.iocp:
        from asyncio.windows_events import ProactorEventLoop
        loop = ProactorEventLoop()
        asyncio.set_event_loop(loop)
    elif args.select:
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    roots = {fix_url(root) for root in args.roots}

    table = Table_Print()
    table.file = args.save_log
    crawler = crawling.Crawler(roots,
                               exclude=args.exclude,
                               strict=args.strict,
                               max_redirect=args.max_redirect,
                               max_tries=args.max_tries,
                               max_tasks=args.max_tasks,
                               robots_txt=args.robots,
                               download_images=args.download_images,
                               table=table
                               )
    try:
        loop.run_until_complete(crawler.crawl())  # Crawler gonna crawl.
    except KeyboardInterrupt:
        sys.stderr.flush()
        print('\nInterrupted\n')
    finally:
        reporting.report(crawler, table=table)
        if args.download_images:
            try:
                image_downloader = File_Downloader()
                # Remove the only unhandled url in the image_urls set: None
                crawler.HTML_parser.image_urls.discard(None)
                # Loops through all of the images found in the web crawler and downloads them
                @asyncio.coroutine
                def async_download():
                    for url in crawler.HTML_parser.image_urls:
                        yield from image_downloader.download_image(url)
                loop.run_until_complete(async_download())
            except KeyboardInterrupt:
                sys.stderr.flush()
                print('\nInterrupted\n')
            finally:
                # Save {image, height, width} obj array into a JSON file for website
                from os import makedirs
                makedirs("../cache_web/", exist_ok=True)
                import json
                json_string_55 = str(image_downloader.json_dl)
                json_string_55 = json_string_55.replace('\'', '\"')
                print_file = open('../cache_web/images.json', 'w')
                print_file.write(json_string_55)
                # print_file.write(json.dumps(str(image_downloader.json_dl)))
                print_file.close()
        crawler.close()
        # next two lines are required for actual aiohttp resource cleanup
        loop.stop()
        loop.run_forever()
        loop.close()

if __name__ == '__main__':
    main()
