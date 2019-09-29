import PySimpleGUI as sg
import ext.pixiv as pixiv
import ext.nhentai as nhentai
import ext.misc as misc
import requests

sess = requests.Session()


def parse_url(url: str, return_details: bool = False):
    if 'pixiv' in url and 'artworks' in url:
        album = pixiv.Illust(url, session=sess)
    elif 'pixiv' in url and 'member' in url:
        album = pixiv.User(url, session=sess)
    elif 'nhentai' in url:
        album = nhentai.Gallery(url, session=sess)
    else:
        raise misc.AlbumNotFoundException

    if return_details is True:
        return repr(album), str(album)
    else:
        album.download()
        sg.PopupOK("Completed.", title="Download operations complete.")


class SiteNotSupportedException(Exception):
    pass


layout = [
    [sg.Text("URL: "), sg.InputText(key='_url_')],
    [sg.Button("Download", key='_download_'),
     sg.Button("Check", key='_check_'),
     sg.Button("Compile folder...", key='_compile_'),
     sg.Cancel()]
]

window = sg.Window("JZ's Image Scraper w/GUI v0.1", layout=layout)

while True:
    event, values = window.Read()
    if event in (None, 'Cancel'):
        break
    else:
        url = values["_url_"]
        try:
            if event == '_check_':
                item = parse_url(url, return_details=True)
                sg.PopupOK(
                    item[0], title=f"Showing results for item of type {item[1]}.")
            elif event == "_download_":
                parse_url(url)
            elif event == "_compile_":
                folder = sg.PopupGetFolder("Select folder to compile...")
                if folder is None:
                    continue
                else:
                    misc.compile_from_folder(folder)

        except misc.AlbumNotFoundException:
            sg.PopupError("Album not found.", title="AlbumNotFoundException")

        except SiteNotSupportedException:
            sg.PopupError("Site not supported!",
                          title="SiteNotSupportedException")

        except pixiv.UserNotAuthorisedException:
            sg.PopupError(
                "An error occured with the Pixiv artwork. \nIf the problem persists, contact the developer.", title="UserNotAuthorisedException")

        except Exception:
            sg.PopupError("An error has occured.", title="Exception")
