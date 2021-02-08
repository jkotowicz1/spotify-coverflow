import time
import requests
import itunespy
import spotipy
import spotipy.util as util
from io import BytesIO
from PIL import Image, ImageTk
from tkinter import Tk, Frame, Label

from pprint import pprint

MONITOR_WIDTH = 1280
MONITOR_HEIGHT = 1024

USERNAME = "1166791506"
SECRET = "ef12bafe03d740df961f483d0562ed72"
SCOPE = "user-read-playback-state"
URI = "http://localhost:8888/callback"
ID = "733f26df73dd4c4e83805e931be8f96b"


def get_token():
    '''
    This will open a new browser window if the developer account information
    above is correct. Follow the instructions that appear in the console dialog.
    After doing this once the token will auto refresh as long as the .cache file exists
    in the root directory.
    '''

    token = util.prompt_for_user_token(USERNAME, SCOPE, ID, SECRET, URI)
    return token


def get_current_playing(token):
    '''
    Returns information about the current playing song. If no song is currently
    playing the most recent song will be returned.
    '''

    spotify = spotipy.Spotify(auth=token)
    results = spotify.current_user_playing_track()

    img_src = results["item"]["album"]["images"][0]["url"]
    artist = results["item"]["album"]["artists"][0]["name"]
    album = results["item"]["album"]["name"]
    name = results["item"]["name"]
    isrc = results["item"]["external_ids"]["isrc"]

    return {
        "img_src": img_src,
        "artist": artist,
        "album": album,
        "name": name,
        "id": isrc
    }


def itunes_search(album, artist):
    '''
    Check if iTunes has a higher definition album cover and
    return the url if found
    '''

    try:
        matches = itunespy.search_album(album)
    except LookupError:
        return None

    for match in matches:
        if artist in match.artist_name:
            if album in match.collection_name:
                return match.artwork_url_100.replace('100x100b', '1024x1024b')
        
        


def convert_image(src):
    '''
    Convert the image url to Tkinter compatible PhotoImage
    '''

    res = requests.get(src)
    img = Image.open(BytesIO(res.content)).resize(
        (1024, 1024), Image.ANTIALIAS)
    pi = ImageTk.PhotoImage(img, size=())

    return pi


def main(token):
    '''
    Main event loop, draw the image and text to tkinter window
    '''

    root = Tk()
    root.configure(bg="black", cursor="none")
    root.attributes('-fullscreen', True)

    f = Frame(root, bg="black", width=MONITOR_WIDTH, height=MONITOR_HEIGHT)
    f.grid(row=0, column=0, sticky="NW")
    f.grid_propagate(0)
    f.update()

    most_recent_song = ""
    while True:
        redraw = True

        time.sleep(5)
        current_song = get_current_playing(token)

        if current_song["album"] != most_recent_song:
            redraw = True
        else:
            redraw = False

        if redraw:
            artist = current_song["artist"]
            name = current_song["name"]
            album = current_song["album"]
            most_recent_song = album
            hd_img = itunes_search(
                current_song["album"], current_song["artist"])

            if hd_img != None:
                pi = convert_image(hd_img)
                itunes_cover = "iTunes Cover"
            else:
                pi = convert_image(current_song["img_src"])
                itunes_cover = ""

            img_x = MONITOR_WIDTH / 2
            img_y = MONITOR_HEIGHT / 2

            label = Label(f, image=pi, highlightthickness=0, bd=0)
            label.place(x=img_x, y=img_y, anchor="center")

            artist_label = Label(
                f,
                text=artist,
                bg="black",
                fg="white",
                font=("Courier New", 10)
            )

            artist_x = MONITOR_WIDTH - (MONITOR_WIDTH / 5)
            artist_y = (MONITOR_HEIGHT / 2) - 50
            artist_label.place(x=artist_x, y=artist_y, anchor="center")

            song_label = Label(
                f,
                text=name + "\n \n " + album + "\n \n "+ itunes_cover,
                bg="black",
                fg="white",
                font=("Courier New", 10),
            )

            song_x = MONITOR_WIDTH - (MONITOR_WIDTH / 5)
            song_y = (MONITOR_HEIGHT / 2) + 50
            song_label.place(x=song_x, y=song_y, anchor="center")

            root.update()

            label.destroy()
            artist_label.destroy()
            song_label.destroy()      


if __name__ == "__main__":
    token = get_token()
    main(token)
