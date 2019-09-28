import requests
from bs4 import BeautifulSoup
import json
import re


class Gallery:

    sess = requests.Session()

    def __init__(self, url):
        self.url = url
        self.details = self.get_details()
        self.category = f'Downloads\\nhentai\\{self.details["artist"][0]}\\{re.search(r"[0-9]+", self.url).group(0)}'

    def __repr__(self) -> str:
        details_str = ''
        for item in self.details:
            details_str += f'{item}: {self.details[item]}\n'
        return details_str

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
                raise AlbumNotFoundException

    def get_page_images(self):
        pages = self.pages_raw
        image_list = []
        for page_url in pages:
            with self.sess.get(page_url) as resp:
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'lxml')
                    image_list.append(
                        soup.find('img', class_='fit-horizontal')["src"])

        self.details["page_images"] = image_list
        return image_list


class AlbumNotFoundException(Exception):
    '''Raised when album cannot be found at specified URL.'''
    pass
