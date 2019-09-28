import requests
from bs4 import BeautifulSoup
import re
import json
import ext.misc as misc


class Illust:

    '''Creates an instance of a pixiv illustration thread. Does not work with R-18 images and copyrighted images.'''

    def __init__(self, url, session: requests.Session = None):
        self.illust_url = url
        self.id = re.search(r'([0-9]+)', self.illust_url).group(0)
        self.sess = session if session is not None else requests.Session()
        self.pages_json = f'https://www.pixiv.net/ajax/illust/{self.id}/pages'
        self.pages_raw = self.get_pages()
        self.details_raw = self.get_detail()

        self.pages = {
            "small": [item["urls"]["small"] for item in self.pages_raw["body"]],
            "regular": [item["urls"]["regular"] for item in self.pages_raw["body"]],
            "original": [item["urls"]["original"] for item in self.pages_raw["body"]]
        }

        self.details = {
            "user_id": self.details_raw["body"][self.id]["userId"],
            "user_name": self.details_raw["body"][self.id]["userName"],
            "illust_url": self.illust_url,
            "illust_title": self.details_raw["body"][self.id]["title"],
            "illust_tags": self.details_raw["body"][self.id]["tags"],
            "illust_description": self.details_raw["body"][self.id]["description"],
            "page_count": len(self.pages_raw["body"])
        }

        self.category = f'Downloads\\pixiv\\[{self.details["user_id"]}] - {self.details["user_name"]}\\[{self.id}] - {self.details["illust_title"]}'

    def __repr__(self):
        details_str = misc.dict_to_str(self.details)
        return details_str

    def get_pages(self) -> dict:
        with self.sess.get(self.pages_json, headers={'referer': self.illust_url}) as page:
            if page.status_code == 200:
                page_content = page.json()
                return page_content
            elif page.status_code == 404:
                raise AlbumNotFoundException

    def get_detail(self) -> dict:
        detail_url = f'https://www.pixiv.net/ajax/user/{self.id}/illusts?ids[]={self.id}'
        with self.sess.get(detail_url) as page:
            if page.status_code == 200:
                return page.json()


class User:
    '''Creates an instance of a pixiv user.'''
    sess = requests.Session()

    def __init__(self, url):
        self.id = re.search(r'([0-9]+)', url).group(0)
        self.url = f'https://www.pixiv.net/member_illust.php?id={self.id}'
        self.illusts_raw = self.get_illusts()
        self.illusts = [
            f'https://www.pixiv.net/en/artworks/{item}' for item in list(self.illusts_raw["body"]["illusts"])]
        self.illusts_count = len(self.illusts)
        self.details = self.get_user_details()

    def __repr__(self):
        details_str = misc.dict_to_str(self.details)
        return details_str

    def get_illusts(self):
        illusts_raw_url = f'https://www.pixiv.net/ajax/user/{self.id}/profile/all'
        with self.sess.get(illusts_raw_url) as page:
            if page.status_code == 200:
                return page.json()
            elif page.status_code == 404:
                raise AlbumNotFoundException

    def get_user_details(self):
        sess = self.sess
        sample_illust = Illust(self.illusts[0], session=sess)
        self.name = sample_illust.details["user_name"]
        artist_details = {
            "name": self.name,
            "id": self.id,
            "profile": self.url,
            "illusts_count": self.illusts_count
        }
        self.details = artist_details
        return artist_details


class AlbumNotFoundException(Exception):
    '''Raised when album is not found. Work may have been deleted, or the ID does not exist.'''
