import os
import re
import json

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
OUTPUT_FILE_NAME = "output.json"
PLAYLIST_FILE_NAME = "playlists.txt"

with open(PLAYLIST_FILE_NAME, "r") as file:
    PLAYLIST_LINKS = file.readlines()

client_credentials_manager = SpotifyClientCredentials(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET
)

session = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

playlists = {}
songs = {}

for playlist_link in PLAYLIST_LINKS:
    if match := re.match(r"https://open.spotify.com/playlist/(.*)\?", playlist_link):
        playlist_uri = match.groups()[0]
    else:
        raise ValueError("Got: {}, Expected format: https://open.spotify.com/playlist/...".format(playlist_link))

    playlist = session.playlist(playlist_uri)

    playlists[playlist["id"]] = {
        "name": playlist["name"],
        "id": playlist["id"],
        "url": playlist["external_urls"]["spotify"],
        "image_url": playlist["images"][0]["url"]
    }

    offset = 0
    tracks = []
    while chunk := session.playlist_tracks(playlist_uri, limit=100, offset=offset)["items"]:
        tracks.extend(chunk)
        offset += 100

    for track in tracks:
        song = track["track"]
        if song["id"] not in songs.keys():
            songs[song["id"]] = {
                "id": song["id"],
                "name": song["name"],
                "url": song["external_urls"]["spotify"],
                "artists": ", ".join([artist["name"] for artist in song["artists"]]),
                "duration": song["duration_ms"],
                "album_name": song["album"]["name"],
                "album_release": song["album"]["release_date"],
                "album_url": song["album"]["external_urls"]["spotify"],
                "image_url": song["album"]["images"][0]["url"],
                "playlists": [playlist["id"]]
            }
        else:
            songs[song["id"]]["playlists"].append(playlist["id"])

output = {
    "playlists": playlists,
    "songs": songs
}

with open(OUTPUT_FILE_NAME, "w") as file:
    file.write(json.dumps(output, indent=4))

# Useful values from track["track"]:
# ["artists"]
#   ["external_urls"]
#       ["spotify"]
#   ["name"]
#   ["id"]
# ["duration_ms"]
# ["external_urls"]
#   ["spotify"]
# ["id"]
# ["name"]
# ["album"]
#   ["external_urls"]
#       ["spotify"]
#   ["id"]
#   ["images"]
#       ...
#           ["url"]
#           ["height"]
#           ["width"]
