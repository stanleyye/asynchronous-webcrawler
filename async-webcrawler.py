#!/usr/bin/env python

import asyncio
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

linksVisited = {}

async def crawl(aLink, originalBaseUrl):

    if ((aLink in linksVisited) or
       (not(aLink.startswith(originalBaseUrl)))):
        return
    else:
        try:
            req = await requests.get(aLink)
        except requests.exceptions.RequestException as e:
            print(e)
            exit()
        else:
            linksVisited[aLink] = 1
            print(aLink)
            print("Status:", req.status_code)

        soup = BeautifulSoup(req.text, "html.parser")

        for link in soup.find_all("a", href=True):
            if (link.get("href").startswith("http")):

                # if case is necessary to prevent printing
                # same link multiple times
                if ((link.get('href') in linksVisited) or
                   (not(aLink.startswith(originalBaseUrl)))):
                    pass
                else:
                    crawl(link.get('href'), originalBaseUrl)

            elif (link.get('href').startswith("javascript:")):
                pass
            else:
                linkFullUrl = urljoin(originalBaseUrl, link.get('href'))

                # if case is necessary to prevent
                # repeated printing of same link
                if ((linkFullUrl in linksVisited) or
                   (not(linkFullUrl.startswith(originalBaseUrl)))):
                    pass
                else:
                    crawl(linkFullUrl, originalBaseUrl)

        for sourceLink in soup.find_all(["img", "script"], src=True):
            if (sourceLink.get("src").startswith("http")):

                if ((sourceLink.get("src") in linksVisited) or
                   (not(aLink.startswith(originalBaseUrl)))):
                    pass
                else:
                    crawl(sourceLink.get("src"), originalBaseUrl)
            else:

                srcLinkFullUrl = urljoin(originalBaseUrl,
                                         sourceLink.get("src"))

                if ((srcLinkFullUrl in linksVisited) or
                   (not(aLink.startswith(originalBaseUrl)))):
                    pass
                else:
                    crawl(srcLinkFullUrl, riginalBaseUrl)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process a domain.")
    parser.add_argument("link")
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    if (args.link.startswith("http://") or args.link.startswith("https://")):
        crawl(args.link, args.link)
    else:
        crawl("http://" + args.link, "http://" + args.link)
    loop.close()

    print("There is a total of", len(linksVisited),
          "links and sources on this domain")
