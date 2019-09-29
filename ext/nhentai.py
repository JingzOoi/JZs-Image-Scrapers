import requests
from bs4 import BeautifulSoup
import json
import re
import ext.misc as misc
import os
import concurrent.futures


class Gallery:

    def __init__(self, url, session: requests.Session = requests.Session()):
        self.url = url
        self.sess = session
        self.details = self.get_details()
        self.category = f'Downloads\\nhentai\\{self.details["artist"][0]}\\{re.search(r"[0-9]+", self.url).group(0)}'
        self.pages = []

    def __repr__(self) -> str:
        details_str = misc.dict_to_str(self.details)
        return details_str

    def __str__(self) -> str:
        return 'NHentai Gallery'

    def get_details(self):
        with self.sess.get(self.url) as resp:
            if resp.status_code == 200:
                webpage = resp.text
                soup = BeautifulSoup(webpage, 'lxml')
                meta = soup.find_all('meta')

                metaDict = {}

                for tag in meta:
                    try:
                        if tag["itemprop"] == "name":
                            metaDict["name"] = tag["content"]
                        elif tag["itemprop"] == "image":
                            metaDict["thumbnail"] = tag["content"]
                    except KeyError:
                        try:
                            if tag["name"] == "twitter:description":
                                metaDict["tags"] = tag["content"].split(
                                    ', ')
                        except KeyError:
                            pass

                metaDict["artist"] = [a.text.split(' (')[0] for a in soup.find_all(
                    'a', class_='tag') if re.match(r'/artist/.+/', a["href"])]

                metaDict["gallery_url"] = self.url

                self.pages_raw = [f'https://nhentai.net{page_thumbnail["href"]}'
                                  for page_thumbnail in soup.find_all("a", class_="gallerythumb")]

                self.details = metaDict

                return metaDict

            elif resp.status_code == 404:
                raise misc.AlbumNotFoundException

    def get_page_image(self, url):
        with self.sess.get(url) as resp:
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'lxml')
                self.pages.append(
                    soup.find('img', class_='fit-horizontal')["src"])

    def get_page_images(self):
        pages = self.pages_raw
        with concurrent.futures.ThreadPoolExecutor(3) as executor:
            executor.map(self.get_page_image, pages)

    def download(self):
        self.get_page_images()
        misc.download_images_from_url_list(
            self.pages, self.category, self.sess)
        with open(os.path.join(self.category, 'metadata.txt'), 'w') as f:
            f.write(self.__repr__())
