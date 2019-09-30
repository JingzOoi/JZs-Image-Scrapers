import requests
from bs4 import BeautifulSoup
import re
import json
import ext.misc as misc
import os


class Thread:
    def __init__(self, url, session: requests.Session = requests.Session()):
        self.url = url
        self.sess = session
        self.details = self.get_details()
        self.category = misc.join_path(
            ['Downloads', 'twitter', self.details["author"], self.details["id"]])

    def __str__(self) -> str:
        return json.dumps(self.details, indent=4, ensure_ascii=False)

    def __repr__(self):
        return 'Twitter Thread'

    def get_details(self):
        with self.sess.get(self.url) as page:
            if page.status_code == 200:
                details = {}
                soup = BeautifulSoup(page.text, 'lxml')

                media_container = soup.find(
                    'div', attrs={'class': 'AdaptiveMediaOuterContainer'})

                self.images = [
                    f'{img["src"]}:orig' for img in media_container.find_all('img')]

                r = r'https:\/\/twitter\.com\/([a-zA-Z0-9_]+)\/status\/([0-9]+)'

                details["author"] = re.match(r, self.url).group(1)
                details["id"] = re.match(r, self.url).group(2)

                details["description"] = soup.find(
                    'p', attrs={'class': 'TweetTextSize--jumbo'}).text

                details["url"] = self.url
                details["image_count"] = len(self.images)

                return details

    def download(self):
        misc.download_images_from_url_list(
            self.images, self.category, self.sess)
        misc.write_metadata(self.category, self.__str__())
