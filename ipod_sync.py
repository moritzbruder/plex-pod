import gpod
import json
from song_repo import SongRepo

repo = SongRepo()
song_ids = [int(id) for id in repo.get_all_song_ids()]

db = gpod.Database("/mnt/ipod")
all_tracks = [track for track in db]

for track in all_tracks:
    plex_key = int(track['userdata']['plex-key_utf8'])
    if plex_key in song_ids:
        print(str(plex_key) + " already exists on iPod")
        song_ids.remove(plex_key)
    else:
        print("Removing " + str(plex_key))
        db.remove(track)


db.copy_delayed_files()
db.close()



db = gpod.Database("/mnt/ipod")

print("\n\n\nUPLOADING\n\n")

for song_id in song_ids:
    print("Adding song w/ id " + str(song_id))
    song = repo.get_song_by_id(str(song_id))
    try:
        track_path = "./.plex-pod-lib/" + str(song_id) + ".mp3"
        track_cover_path = "./.plex-pod-lib/" + str(song_id) + "_cover.jpeg"
        print("  path:" + track_path)
        track = db.new_Track(filename=track_path)
        track['artist'] = song['artist']
        track['album'] = song['album']
        track['title'] = song['title']
        track._set_userdata_utf8("plex-key", song['id'])
        #track['userdata']['plex-key'] = song['id']
        track.set_coverart_from_file(track_cover_path)
        track.copy_to_ipod()
    except gpod.TrackException, e:
        print e
        continue # skip this track


db.close()