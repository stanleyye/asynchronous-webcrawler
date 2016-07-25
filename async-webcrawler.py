#!/usr/bin/env python

import asyncio
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

linksVisited = {}
linkSrcVisited = {}


async def crawl(aLink, originalBaseUrl):

    if ((aLink in linksVisited) or
       (not(aLink.startswith(originalBaseUrl)))):
        return
    else:
        try:
            req = requests.get(aLink)
        except requests.exceptions.RequestException as e:
            print(e)
            exit()
        else:
            linksVisited[aLink] = 1

        soup = BeautifulSoup(req.text, "html.parser")

        for link in soup.find_all("a", href=True):
            if (link.get("href").startswith("http")):

                try:
                    linkReq = requests.get(link.get('href'))
                except requests.exceptions.RequestException as e:
                    print("The server couldn't fulfill the request for link:",
                          link.get('href'), "Status:", e)
                else:
                    # if case is necessary to prevent printing
                    # same link multiple times
                    if ((link.get('href') in linksVisited) or
                       (not(aLink.startswith(originalBaseUrl)))):
                        pass
                    else:
                        linksVisited[link.get('href')] = 1
                        print(link.get('href'))
                        print("Status:", linkReq.status_code)
                        crawl(link.get('href'), originalBaseUrl)

            elif (link.get('href').startswith("javascript:")):
                pass
            else:
                linkFullUrl = urljoin(originalBaseUrl, link.get('href'))

                try:
                    linkReq = requests.get(linkFullUrl)
                except requests.exceptions.RequestException as e:
                    print("The server couldn't fulfill the request for link:",
                          linkFullUrl, "Status:", e)
                else:
                    # if case is necessary to prevent
                    # repeated printing of same link
                    if ((linkFullUrl in linksVisited) or
                       (not(linkFullUrl.startswith(originalBaseUrl)))):
                        pass
                    else:
                        linksVisited[linkFullUrl] = 1
                        print(linkFullUrl)
                        print("Status:", linkReq.status_code)
                        crawl(linkFullUrl, originalBaseUrl)

        for sourceLink in soup.find_all(["img", "script"], src=True):
            if (sourceLink.get("src").startswith("http")):
                try:
                    sourceLinkReq = requests.get(sourceLink.get("src"))
                except requests.exceptions.RequestException as e:
                    print("The server couldn't fulfill the request for link:",
                          sourceLink.get("src"), "Status:", e)
                else:
                    if ((sourceLink.get("src") in linkSrcVisited) or
                       (not(aLink.startswith(originalBaseUrl)))):
                        pass
                    else:
                        linkSrcVisited[sourceLink.get("src")] = 1
                        print(sourceLink.get("src"))
                        print("Status:", sourceLinkReq.status_code)
                        crawl(sourceLink.get("src"), originalBaseUrl)
            else:

                srcLinkFullUrl = urljoin(originalBaseUrl,
                                         sourceLink.get("src"))

                try:
                    sourceLinkReq = requests.get(srcLinkFullUrl)
                except requests.exceptions.RequestException as e:
                    print("The server couldn't fulfill the request for link:",
                          srcLinkFullUrl, "Status:", e)
                else:
                    if ((srcLinkFullUrl in linkSrcVisited) or
                       (not(aLink.startswith(originalBaseUrl)))):
                        pass
                    else:
                        linkSrcVisited[srcLinkFullUrl] = 1
                        print(srcLinkFullUrl)
                        print("Status:", sourceLinkReq.status_code)
                        crawl(srcLinkFullUrl, originalBaseUrl)

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
    print("There is a total of", len(linksVisited), "links on this domain")
    print("There is a total of", len(linkSrcVisited), "sources on this domain")
