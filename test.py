#!/usr/bin/env python

import asyncio
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

count = 0
linksVisited = {}
q = asyncio.Queue()


async def consumeLinks():
    print("consume links")
    while (True):
        value = await q.get()
        print(value[0])
        print("Status:", value[1].status_code)



def crawl(aLink, originalBaseUrl):

    if ((aLink in linksVisited) or
       (not(aLink.startswith(originalBaseUrl)))):
        return
    else:
        try:
            # run the request in a different thread
            # futureReq = loop.run_in_executor(None, requests.get, aLink)
            # req = await futureReq

            req = requests.get(aLink)
            print(count)


        except requests.exceptions.RequestException as e:
            print(e)
            exit()
        else:
            q.put([aLink, req])
            linksVisited[aLink] = 1

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
                        crawl(srcLinkFullUrl, originalBaseUrl)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process a domain.")
    parser.add_argument("link")
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    if (args.link.startswith("http://") or args.link.startswith("https://")):
        loop.create_task(crawl(args.link, args.link))
    else:
        loop.create_task(crawl("http://" + args.link,
                                      "http://" + args.link))

    loop.create_task(consumeLinks())
    loop.run_forever()

    print("There is a total of", len(linksVisited),
          "links and sources on this domain")
