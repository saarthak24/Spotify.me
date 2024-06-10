import spotipy
from spotipy.oauth2 import SpotifyOAuth

import json

from secret import *

scope = "user-library-read playlist-read-private"

def store_all_saved_tracks(sp, filename: str):
    """
    Retrieves and stores all of the user's saved/liked tracks in a JSON file (if it doesn't already exist).

    Parameters:
        sp (Spotify client): A Spotify client object for interacting with the Spotify API.
        filename (str): The name of the (JSON) file where the tracks will be stored.

    Returns:
        list: A list of saved tracks, if the file did not previously exist and tracks were stored successfully to the newly created file.
        None: If the file already exists or no tracks are saved.
    """

    try:
        # Attempt to open the file in read mode
        with open(filename, 'r') as f:
            print(f"The file '{filename}' already exists.")
            return None
    except FileNotFoundError:
        # File does not exist, so retrieve the user's saved tracks
        '''
        Example "results":

        Key:  href
        Value:  https://api.spotify.com/v1/me/tracks?offset=0&limit=20
        Key:  items
        Value: (a dict of this user's 20 latest saved tracks)
        Key:  limit
        Value:  20
        Key:  next
        Value:  https://api.spotify.com/v1/me/tracks?offset=20&limit=20
        Key:  offset
        Value:  0
        Key:  previous
        Value:  None
        Key:  total
        Value:  5591 (the total amount of this user's saved tracks)
        '''

        results = sp.current_user_saved_tracks()
        tracks = results['items']
        # Continue retrieving tracks until all of the user's saved tracks have been retrieved
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])

        # Save the tracks to a JSON file if there are any tracks
        if tracks: # tracks is a list of dictionaries
            for t in tracks:
                if "available_markets" in t['track']:
                    del t['track']['available_markets']
                if "available_markets" in t['track']['album']:
                    del t['track']['album']['available_markets']
            with open(filename, 'w') as f:
                json.dump(tracks, f, indent=4)
            print(f"Tracks successfully saved to '{filename}'.")
            return tracks
        else:
            print("No tracks to save.")
            return None
        
def update_saved_tracks(sp, filename: str):
    try:
        # Check if saved_tracks.json exists
        with open(filename, 'r+') as f:
            print(f"'{filename}' exists, attempting to update it with any newly saved tracks")
            data = json.load(f)
            most_recent_saved_track_uri = data[0]['track']['uri']
            print("URI of the first (most recently saved) track:", most_recent_saved_track_uri)
            tracks_to_add = []
            results = sp.current_user_saved_tracks(limit=1)
            cur_track = results['items'][0]
            while(cur_track['track']['uri'] != most_recent_saved_track_uri and results['next']):
                if "available_markets" in cur_track['track']:
                    del cur_track['track']['available_markets']
                if "available_markets" in cur_track['track']['album']:
                    del cur_track['track']['album']['available_markets']
                tracks_to_add.append(cur_track)
                results = sp.next(results)
                cur_track = results['items'][0]
            # Combine the new data for saved tracks with the old/existing data for saved tracks
            updated_data = tracks_to_add + data
            # Move the file pointer to the beginning of the file to overwrite from start
            f.seek(0)
            # Write the combined data back to the file
            json.dump(updated_data, f, indent=4)
            # Truncate the file to remove any leftover data
            f.truncate()
    except FileNotFoundError:
        store_all_saved_tracks(sp, filename)

# TODO: Write function to retrieve and store the user's playlists

def main():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                client_secret=SPOTIPY_CLIENT_SECRET,
                                                redirect_uri=SPOTIPY_REDIRECT_URI,
                                                scope=scope))
    
    filename = "saved_tracks.json"
    # store_all_saved_tracks(sp, filename)
    update_saved_tracks(sp, filename)

if __name__ == '__main__':
    main()
    