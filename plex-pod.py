import json
import os
import urllib.request

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from plexapi.server import PlexServer
from datetime import datetime
from art import tprint

from song_repo import SongRepo

config = json.loads(open("/etc/plex-pod.json", "r").read())

plex = PlexServer(config["server"]["url"], config["server"]["token"])

scheduler = BlockingScheduler()
repo = SongRepo()

tprint("plex-pod")

print("Using server \"" + plex.friendlyName + "\"")

lib_key = config["libraryKey"]
lib_section = [p for p in plex.library.sections() if p.key == lib_key][0]
print("Using Library \"" + lib_section.title + "\" (" + str(lib_section.key) + ")")

playlist_key = config["playlistKey"]
playlist = [p for p in lib_section.playlists() if p.ratingKey == playlist_key][0]
print("Using Playlist \"" + playlist.title + "\" (" + str(playlist.ratingKey) + ")")

print("\n\n\n")


def track_to_dict(track):
    return {
        "id": str(track.ratingKey),
        "title": track.title,
        "album": track.album().title,
        "artist": track.album().artist().title,
        "track_no": track.trackNumber
    }


def find_songs_to_download():
    existing_song_keys = repo.get_all_song_ids()
    return [track for track in playlist.items() if str(track.ratingKey) not in existing_song_keys]


def find_song_ids_to_remove():
    existing_song_keys = repo.get_all_song_ids()
    playlist_song_keys = [str(track.ratingKey) for track in playlist.items()]
    return [track for track in existing_song_keys if track not in playlist_song_keys]


@scheduler.scheduled_job(IntervalTrigger(seconds=config.get("syncIntervalSeconds", 15 * 60)))
def sync_from_plex():
    print("\n\n============================================\nStarting sync at", datetime.now())

    dl_dir = "./.plex-pod-lib/.downloading"
    os.makedirs(name=dl_dir, exist_ok=True)
    dl_count = 0

    def clear_downloading():
        for f in os.listdir(dl_dir):
            os.remove(dl_dir + "/" + f)

    songs_to_remove = find_song_ids_to_remove()
    if len(songs_to_remove) > 0:
        print("-- Deleting ", len(songs_to_remove), " songs.")
    for track_id in songs_to_remove:
        try:
            os.remove("./.plex-pod-lib/" + track_id + ".mp3")
            os.remove("./.plex-pod-lib/" + track_id + "_cover.jpeg")
        finally:
            repo.remove_song(track_id)

    songs_to_dl = find_songs_to_download()
    for track in songs_to_dl:
        dl_count += 1
        print("-- Downloading track", dl_count, "of", len(songs_to_dl), ": ", track.title, "by", track.album().artist().title)
        key = track.ratingKey
        fname = "./.plex-pod-lib/" + str(key) + ".mp3"
        if track.thumb is not None:
            cover_url = plex.transcodeImage(track.thumb, 300, 300)
            urllib.request.urlretrieve(cover_url, "./.plex-pod-lib/" + str(key) + "_cover.jpeg")

        clear_downloading()
        track.download(dl_dir)
        downloaded = dl_dir + "/" + os.listdir(dl_dir)[0]
        os.rename(downloaded, fname)
        repo.add_song(track_to_dict(track))

    if len(songs_to_dl) == 0:
        print("-- No songs to download")

    print("- Sync completed.\n============================================\n")


scheduler.start()
