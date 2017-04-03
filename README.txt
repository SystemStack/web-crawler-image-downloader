Fork from https://github.com/aosabook/500lines/tree/master/crawler

Author: Levi Broadnax
Project: Web Crawler/Generator
Requirements:
  * Python 3.4+
  * aiohttp 0.21
  * Pillow

## Additions:
* Readable CLI Output
* Optional file output for log
* Robots.txt compliance
* HTML Parsing to download images from target
* Generates a simple site with those images
* More consistent 500 error handling 

Install the crawler's requirements like:

    python -m pip install -r requirements.txt

Example command line:

    python crawl.py xkcd.com -d

Use --help to see all options.

 
