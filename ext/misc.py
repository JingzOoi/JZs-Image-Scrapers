import requests
import os
from time import sleep
import shutil


class AlbumNotFoundException(Exception):
    '''Raised when album is not found. Work may have been deleted, or the ID does not exist.'''


def list_to_str(list_: list) -> str:
    list_str = ''
    for item in list_:
        list_str += f'{item}'
        if item != list_[-1]:
            list_str += '\n'
    return list_str


def dict_to_str(dict_: dict) -> str:
    dict_str = ''
    for item in list(dict_):
        dict_str += f'{item}: {dict_[item]}'
        if item != list(dict_)[-1]:
            dict_str += '\n'
    return dict_str


class Image:

    def __init__(self, url: str, category: str,  session: requests.Session = requests.Session(), name: str = None):
        self.url = url
        self.category = category
        self.name = f'{name}{os.path.splitext(self.url)[-1]}' if name is not None else os.path.basename(
            self.url)
        self.sess = session

    def get_image(self):
        with self.sess.get(self.url, headers={"referer": self.url}) as page:
            if page.status_code == 200:
                self.size = len(page.content)
                self.time = page.elapsed.total_seconds()
                return page.content

    def get_details(self) -> dict:
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


def download_image_from_url(url, category, session):
    img = Image(url, category, session=session)
    img.download()


def download_images_from_url_list(images_url_list: list, category: str, session: requests.Session = requests.Session()):
    sess = session
    for image_url in images_url_list:
        download_image_from_url(image_url, category, sess)


def compile_from_folder(folder_path):
    folders = os.listdir(folder_path)

    compilation_folder = os.path.join(folder_path, 'compilation')

    os.makedirs(compilation_folder, exist_ok=True)

    whitelist = ['metadata.txt', 'compilation']

    for folder in folders:
        src = os.path.join(folder_path, folder)
        files = os.listdir(src)
        for file in files:
            if file not in whitelist:
                try:
                    shutil.copyfile(os.path.join(src, file),
                                    os.path.join(compilation_folder, file))
                except PermissionError as e:
                    print(f'Overlooking Permission Error in {e}')
                    continue
                except shutil.SameFileError:
                    continue
