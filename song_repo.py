import json

db_dir = "./.plex-pod-lib/songs.json"


class SongRepo:

    def __init__(self):
        try:
            self.songs = json.loads(open(db_dir, "r").read())
        except:
            self.songs = {}

    def add_song(self, song):
        self.songs[song["id"]] = song
        self.write_self()

    def remove_song(self, song_id):
        del self.songs[song_id]
        self.write_self()

    def get_all_song_ids(self):
        return list(self.songs.keys())

    def get_song_by_id(self, id):
        return self.songs[id]

    def write_self(self):
        with open(db_dir, 'w') as f:
            f.write(json.dumps(self.songs))