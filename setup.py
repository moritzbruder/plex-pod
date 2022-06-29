import json

import inquirer
from plexapi.exceptions import PlexApiException
from plexapi.server import PlexServer

global plex

# todo use rpevious config as base for configuration and use as defaults when asking
#  (also: don't override e.g. sync interval)


def get_creds(url=None, token=None):
    auth_answers = inquirer.prompt([
        inquirer.Text("server_base_url", message="Enter the base url of your plex server:", default=url),
        inquirer.Text("server_token", message="Please enter the token to your plex server", default=token),
    ])
    server_base_url = auth_answers["server_base_url"]
    server_token = auth_answers["server_token"]

    global plex
    try:
        plex = PlexServer(server_base_url, server_token)
        return {
            "url": server_base_url,
            "token": server_token
        }
    except PlexApiException as err:
        print("Could not connect to plex. Please try again.", str(err))
        return get_creds(server_base_url, server_token)


creds = get_creds()

library_answer = inquirer.prompt([
    inquirer.List("library", message="Which library is your playlist in?", choices=plex.library.sections())
])

library = library_answer["library"]

playlist_answer = inquirer.prompt([
    inquirer.List("playlist", message="Which playlist do you want to sync?", choices=library.playlists())
])

playlist = playlist_answer["playlist"]

final_config = {
    "server": {
        "url": creds["url"],
        "token": creds["token"]
    },
    "libraryKey": library.key,
    "playlistKey": playlist.ratingKey,
    "syncIntervalSeconds": 15 * 60,
    "syncDirectory": "/var/plex-pod"
}

config_json = json.dumps(final_config, indent=2)

print('\n\nSaving new config to /etc/plex-pod/config.json:\n\n' + config_json + '\n\n')

with open("/etc/plex-pod.json", 'w') as f:
    f.write(config_json)