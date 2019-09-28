import requests
import os
from time import sleep


def list_to_str(list_: list) -> str:
    string = ''
    for item in list_:
        string += f'{item}'
    return string


class Image:

    sess = requests.Session()

    def __init__(self, url: str, category: str, name: str = None):
        self.url = url
        self.category = category
        self.name = f'{name}{os.path.splitext(self.url)[-1]}' if name is not None else os.path.basename(
            self.url)

    def get_image(self):
        with self.sess.get(self.url, headers={"referer": self.url}) as page:
            if page.status_code == 200:
                self.size = len(page.content)
                self.time = page.elapsed.total_seconds()
                return page.content

    def get_details(self):
        content = self.get_image()
        return {"file_size": len(content)}

    def download(self):
        image = self.get_image()
        os.makedirs(self.category, exist_ok=True)
        with open(os.path.join(self.category, self.name), 'wb') as f:
            f.write(image)


def loadingBar(maximumNumber, currentNumber, startingNumber=0, message=''):
    p = ((currentNumber-startingNumber)/(maximumNumber-startingNumber))*100
    load = f"[{('█'*(round(p/100*20))).ljust(20, '.')}] {str(round(p, 2)).ljust(6)}% | {message}"
    print('\b'*len(load), end='', flush=True)
    print(load, end='')


def batch_download(image_url_list, image_category, show_progress=False):
    total = len(image_url_list)
    total_content, total_time = 0, 0
    for num, image_url in enumerate(image_url_list, start=1):
        img = Image(image_url, image_category)
        img.download()
        total_content += img.size
        total_time += img.time
        sleep(img.time)
        if show_progress is True:
            loadingBar(
                maximumNumber=len(image_url_list),
                currentNumber=num,
                message=f'{num}/{total} - {img.name} ({round((total_content/total_time)/1000, 2):,} kb/s)')
    if show_progress is True:
        print('\n')
