import requests
from bs4 import BeautifulSoup
import re
import json
from random import randint


class Illust:

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
        details_str = ''
        for item in self.details:
            details_str += f'{item}: {self.details[item]}\n'
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


class AlbumNotFoundException(Exception):
    '''Raised when album is not found. Work may have been deleted, or the ID does not exist.'''
