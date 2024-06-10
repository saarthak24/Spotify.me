import spotipy
from spotipy.oauth2 import SpotifyOAuth

import datetime

from secret import *

scope = "user-library-read playlist-read-private playlist-modify-public playlist-modify-private"

CURRENT_YEAR = datetime.datetime.now().year

#TODO: Update this file to use saved_tracks.json instead of retrieving the user's saved tracks each time they try to create their throwback playlist
#TODO: Rename this file to a more fitting filename

# Legacy function for retrieving all of the user's saved tracks using an sp object
def get_all_saved_tracks(sp):
    results = sp.current_user_saved_tracks()
    tracks = results['items']
    while results['next']:  # Continue retrieving tracks while there is a next page
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

# Helper function to be used for debugging purposes
def show_tracks(results):
    for item in results['items']:
        track = item['track']
        print("%32.32s %s" % (track['artists'][0]['name'], track['name']))

def get_saved_tracks_from_file(sp, filename: str):
    try:
        # Check if saved_tracks.json exists
        with open(filename, 'r') as f:
            # TODO: finish writing this function
            print(f"'{filename}' exists, attempting to retrieve, store, and return saved tracks from it")
            data = json.load(f)
            return
    except FileNotFoundError:
        store_all_saved_tracks(sp, filename)

def parse_tracks(results):
    # TODO: Modify this function to take in an sp object
    for item in results['items']:
        track = item['track']
        name = track['name']
        albumReleaseDate = track['album']['release_date']
        albumReleaseYear = albumReleaseDate[:4]
        if(CURRENT_YEAR - int(albumReleaseYear) > 10):
            print("%s (%s)" % (name, albumReleaseYear))

def check_for_playlist(sp, playlistName):
    user_playlists = sp.user_playlists(sp.me()['id'])
    print("Searching for the playlist \"%s\"!" % (playlistName))
    # Loop through each playlist in the 'items' list
    for playlist in user_playlists['items']:
        if playlist['name'] == playlistName:
            print("Found the playlist \"%s\"!" % (playlistName))
            return playlist['id']
    print("Could not find the playlist \"%s\"!" % (playlistName))
    return None # Return None if no matching playlist name is found

# Throw it back (10+ years ago)
# Throwback (20+ years ago)
# Antiques (Before 07/06/2000)
def create_throwback_playlist(sp, playlistName):
    '''
    user_playlist_create(user, name, public=True, collaborative=False, description='')

    Creates a playlist for a user

    Parameters:
            user - the id of the user
            name - the name of the playlist
            public - is the created playlist public
            collaborative - is the created playlist collaborative
            description - the description of the playlist
    '''
    if(playlistName == "Throw it back"):
        isPublic = False
        isCollaborative = False
        playlistDesc = 'old, but not old enough to be classy (made with love using spotify.me)'
    if(playlistName == "Throwback"):
        isPublic = True
        isCollaborative = False
        playlistDesc = 'the good ol\' days (made with love using spotify.me)'
    if(playlistName == "Antiques"):
        isPublic = True
        isCollaborative = False
        playlistDesc = 'proof that some things are worth reminiscing over (made with love using spotify.me)'
    print("Attempting to create the playlist \"%s\"!" % (playlistName))
    sp.user_playlist_create(sp.me()['id'], playlistName, public=isPublic, collaborative=isCollaborative, description=playlistDesc)
    print("Successfully created the playlist \"%s\"!" % (playlistName))

def populate_throwback_playlist(sp, playlistName, playlistID):
    tracksToAdd = []
    allSavedTracks = get_all_saved_tracks(sp)

    for item in allSavedTracks:
        track = item['track']
        uri = track['uri']
        name = track['name']
        albumReleaseDate = track['album']['release_date']
        albumReleaseYear = albumReleaseDate[:4]

        # Throw it back (10+ years ago)
        if playlistName == "Throw it back" and (CURRENT_YEAR - int(albumReleaseYear) > 10):
            print(f"{name} ({albumReleaseYear})")
            tracksToAdd.insert(0, uri)
        # Throwback (20+ years ago)
        elif playlistName == "Throwback" and (CURRENT_YEAR - int(albumReleaseYear) > 20):
            print(f"{name} ({albumReleaseYear})")
            tracksToAdd.insert(0, uri)
        # Antiques (Before the year 2000)
        elif playlistName == "Antiques" and (int(albumReleaseYear) < 2000):
            print(f"{name} ({albumReleaseYear})")
            tracksToAdd.insert(0, uri)

    # Add the filtered tracks list (tracksToAdd) to the playlist with the provided playlistID
    while(len(tracksToAdd) > 100): # A maximum of 100 items/tracks can be added in one request.
        sp.playlist_add_items(playlistID, tracksToAdd[0:100])
        tracksToAdd = tracksToAdd[100:]
    if(tracksToAdd): # Add remaining items/tracks, if any
        sp.playlist_add_items(playlistID, tracksToAdd)

def update_throwback_playlist(sp, playlistName, playlistID):
    #TODO: check if any new tracks have been added to the user's saved tracks.
        # if any of these tracks fulfil the filter restrictions for the provided throwback playlist
            # add them to the playlist without modifying existing tracks in the playlist
    return

def main():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                client_secret=SPOTIPY_CLIENT_SECRET,
                                                redirect_uri=SPOTIPY_REDIRECT_URI,
                                                scope=scope))

    playlistToCreate = "Antiques"
    created = check_for_playlist(sp, playlistToCreate)
    # if the playlist already exists, update it as necessary
    if created:
        print(created)
        update_throwback_playlist(sp, playlistToCreate, created)
        return
    # if the playlist does not exist, create it and then populate it
    else:
        while not created:
            create_throwback_playlist(sp, playlistToCreate)
            created = check_for_playlist(sp, playlistToCreate)
        print(created)
        populate_throwback_playlist(sp, playlistToCreate, created)

    # Code to parse through and print out all of the user's saved/liked tracks
    # results = sp.current_user_saved_tracks()
    # parse_tracks(results)
    # while results['next']: # Keep calling the API to retrieve the user's saved tracks until all tracks have been iterated
    #     results = sp.next(results)
    #     parse_tracks(results)

if __name__ == '__main__':
    main()
