# image-board-extensions
An improvised version of my other repo here https://github.com/JingzOoi/JZs-Web-Scrapers. Less text, more returns.
Made this repo because that other one had too much unnecessary stuff I've added in over the weeks that I can't fix. It still works, just looks terrible.

Aiming to have this version print nothing from their extension files, just returns the values that you need. Made the GUI main file if you don't want to work in the command line. Won't judge.

# Currently supports:
<ol>
    <li> pixiv.net </li>
    <li> nhentai.net </li>
    <li> danbooru.donmai.us </li>
</ol>

# How to install and use (GUI):
<ol>
    <li>make sure you have at least python 3.6 installed</li>
    <li>download and extract zip to folder</li>
    <li>open powershell in folder (shift + right click)</li>
    <li>install requirements using "pip install -r requirements.txt" (for first time users)</li>
    <li>type "python mainGUI.py" and press enter</li>
    <li>window should pop up and ready to use</li>
</ol>

# Features:
<ol>
    <li>Download images from popular image boards with high quality</li>
</ol>

# Limitations:
Pixiv doesn't allow un-logined clients to view r-18 or copyrighted data, so that's a no go.

Still figuring outhow to integrate a loading bar using pySimpleGUI with current setup.