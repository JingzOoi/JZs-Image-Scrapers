import requests
from bs4 import BeautifulSoup
import re
import json
import ext.misc as misc
import os
import concurrent.futures


class Post:
    def __init__(self, url: str, session: requests.Session = requests.Session()):
        self.url = url
        self.sess = session
        self.details = self.get_details()

    def __str__(self):
        return json.dumps(self.details, indent=4, ensure_ascii=False)

    def __repr__(self):
        return 'Danbooru Post'

    def get_details(self):
        with self.sess.get(self.url) as page:
            if page.status_code == 200:

                post_details = {}

                soup = BeautifulSoup(page.text, 'lxml')
                post_sidebar = soup.find('aside', attrs={'id': 'sidebar'})

                post_details["copyright"] = self.find_tags(
                    post_sidebar, 'copyright-tag-list')
                post_details["characters"] = self.find_tags(
                    post_sidebar, 'character-tag-list')
                post_details["artists"] = self.find_tags(
                    post_sidebar, 'artist-tag-list')
                post_details["tags"] = self.find_tags(
                    post_sidebar, 'general-tag-list')

                info_section = post_sidebar.find(
                    'section', attrs={'id': 'post-information'})

                post_details["id"] = info_section.find(
                    'li', attrs={'id': 'post-info-id'}).text.split(': ')[-1]
                post_details["size"] = info_section.find(
                    'li', attrs={'id': 'post-info-size'}).a.text.split(': ')[-1]
                post_details["source"] = info_section.find(
                    'li', attrs={'id': 'post-info-source'}).a.attrs["href"]
                post_details["rating"] = info_section.find(
                    'li', attrs={'id': 'post-info-rating'}).text.split(': ')[-1]
                post_details["score"] = info_section.find(
                    'li', attrs={'id': 'post-info-score'}).span.text

                potential_image_url = info_section.find(
                    'li', attrs={'id': 'post-info-size'}).a.attrs["href"]

                if potential_image_url.endswith('.zip'):
                    post_details["image_url"] = soup.find('video').attrs["src"]
                else:
                    post_details["image_url"] = potential_image_url

                return post_details

            elif page.status_code == 404:
                raise misc.AlbumNotFoundException

    @staticmethod
    def find_tags(section, class_name):
        tags = section.find('ul', attrs={'class': class_name})
        return [tag.text for tag in tags.find_all('a', {'class': 'search-tag'})]

    def download(self, category: str = None):
        category = f'Downloads\\danbooru\\Roaming\\{self.details["id"]}' if category is None else category
        url = self.details["image_url"]
        rename = f'danbooru - {self.details["id"]}'
        misc.Image(url, category=category,
                   session=self.sess, name=rename).download()


class Collection:
    def __init__(self, url, session: requests.Session = requests.Session()):
        self.url = url
        self.sess = session
        tags = re.search(
            r'https:\/\/danbooru\.donmai\.us\/posts\?tags=([a-zA-z+0-9-~%]+)', self.url).group(1).split('+')
        self.tags = list(filter(None, tags))
        self.category = f'Downloads\\danbooru\\{"+".join(self.tags)}'

    def __str__(self):
        return json.dumps({'url': self.url, 'tags': self.tags}, indent=4, ensure_ascii=False)

    def __repr__(self):
        return 'Danbooru Collection'

    def get_post_list(self, num: int = 20, show_progress: bool = False):
        post_list = []
        page_num = 1
        while len(post_list) < num:
            url = f'{self.url}&page={page_num}'
            with self.sess.get(url) as page:
                if page.status_code == 200:
                    soup = BeautifulSoup(page.text, 'lxml')

                    post_container = soup.find(
                        'div', attrs={'id': 'posts-container'})

                    if 'Nobody here but us chickens!' not in post_container.text:

                        for post in post_container.find_all('a'):
                            if len(post_list) < num and re.match(r'/posts/[0-9]+', post.attrs["href"]):
                                post_list.append(
                                    f'https://danbooru.donmai.us{post.attrs["href"]}')
                    else:
                        break

                    if show_progress is True:
                        print(
                            f'Currently on page {page_num}. {len(post_list)} images found.')

                    page_num += 1

        self.posts = post_list
        return post_list

    def convert_post_url_to_post_instance_then_download(self, post_url):
        sess = self.sess
        post = Post(post_url, session=sess)
        post.download(category=f'{self.category}\\{post.details["rating"]}')

    def download(self, num: int = 20):
        post_list = self.get_post_list(num)
        with concurrent.futures.ThreadPoolExecutor(3) as executor:
            executor.map(
                self.convert_post_url_to_post_instance_then_download, post_list)

        misc.write_metadata(self.category, self.__str__())
