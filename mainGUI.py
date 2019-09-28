import PySimpleGUI as sg
import ext.pixiv as pixiv
import ext.nhentai as nhentai
from ext.misc import Image
from time import sleep
import os


def batch_download_GUI(image_url_list: list, item):
    image_category = item.category
    metadata = str(item)
    total = len(image_url_list)
    total_content, total_time = 0, 0
    for num, image_url in enumerate(image_url_list, start=1):
        img = Image(image_url, image_category)
        img.download()
        total_content += img.size
        total_time += img.time
        t = sg.OneLineProgressMeter(
            "Downloading image(s)...",
            num,
            total,
            '_one_line_',
            f"{round((total_content/total_time)/1000, 2):,} kb/s",
            orientation='h',

        )
        if t is False:
            break
        sleep(img.time)
    with open(os.path.join(image_category, 'metadata.txt'), 'w') as f:
        f.write(metadata)
    sg.PopupOK(
        f"Done!\nDownload folder: \n{image_category}", title="Downloading complete")


def parse_url(url, return_details: bool = False):

    if 'pixiv.net' in url:
        try:
            illust = pixiv.Illust(url)
        except pixiv.AlbumNotFoundException:
            raise pixiv.AlbumNotFoundException
        else:
            if return_details is True:
                return illust, 'pixiv'
            else:
                batch_download_GUI(illust.pages["original"], illust)

    elif 'nhentai.net' in url:
        try:
            gallery = nhentai.Gallery(url)
        except nhentai.AlbumNotFoundException:
            raise nhentai.AlbumNotFoundException
        else:
            if return_details is True:
                return gallery, 'nhentai'
            else:
                batch_download_GUI(gallery.get_page_images(), gallery)

    else:
        sg.PopupError("Site not supported!")


layout = [
    [sg.Text("URL: "), sg.InputText(key='_url_')],
    [sg.Ok(), sg.Button("Check", key='_check_'), sg.Cancel()]
]

window = sg.Window("JZ's Image Scraper w/GUI v0.1", layout=layout)

while True:
    event, values = window.Read()
    if event in ('None', 'Cancel'):
        break
    elif event == '_check_':
        url = values['_url_']
        try:
            details = parse_url(url, return_details=True)
        except:
            sg.PopupError("Album not found!")
        else:
            sg.PopupOK(details[0], title=f"Details for {details[1]} item")
    elif event == 'Ok':
        url = values['_url_']
        try:
            parse_url(url)
        except:
            sg.PopupError("Album not found!")
