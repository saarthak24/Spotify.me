import spotipy
from spotipy.oauth2 import SpotifyOAuth

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler

from secret import *
from spoti import *


def euclidean_distance(vec1, vec2):
    return np.sqrt(np.sum((vec1 - vec2)**2))

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def find_most_similar_songs(ref_playlist_df, compare_playlist_df, n_similar=5, method='euclidean'):
    # Columns to use for comparison
    feature_cols = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 
                    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']
    
    # Standardize the features
    scaler = StandardScaler()
    ref_scaled = scaler.fit_transform(ref_playlist_df[feature_cols])
    compare_scaled = scaler.transform(compare_playlist_df[feature_cols])
    
    similarities = []
    for i, ref_song in enumerate(ref_scaled):
        for j, comp_song in enumerate(compare_scaled):
            if method == 'euclidean':
                sim = -euclidean_distance(ref_song, comp_song)  # Negative because smaller distance means more similar
            else:
                sim = cosine_similarity(ref_song, comp_song)
            similarities.append((i, j, sim))
    
    # Sort similarities (highest first for cosine, lowest first for euclidean)
    similarities.sort(key=lambda x: x[2], reverse=(method != 'euclidean'))
    
    # Get top N similar pairs
    top_similar = similarities[:n_similar]
    
    return top_similar

def get_playlist_tracks(sp, playlistID):
    results = sp.playlist_items(playlistID)
    tracks = results['items']
    while results['next']: # Continue retrieving tracks while there is a next page
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def main():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                   client_secret=SPOTIPY_CLIENT_SECRET,
                                                   redirect_uri=SPOTIPY_REDIRECT_URI,
                                                   scope=scope))
    
    playlistName = "yerr"

    # Reference playlist
    ref_playlist_id = check_for_playlist(sp, playlistName)
    if not ref_playlist_id:
        return
    ref_tracks = get_playlist_tracks(sp, ref_playlist_id)
    ref_analysis = {}
    for track in ref_tracks:
        try:
            ref_analysis[track['track']['name']] = sp.audio_features(track['track']['uri'])[0]
        except:
            print("An exception occurred while processing the song: " + track['track']['name'])

    print()
    playlistName = "Run It Back"
    
    # Comparison playlist
    compare_playlist_id = check_for_playlist(sp, playlistName)
    if not compare_playlist_id:
        return
    compare_tracks = get_playlist_tracks(sp, compare_playlist_id)
    compare_analysis = {}
    for track in compare_tracks:
        try:
            compare_analysis[track['track']['name']] = sp.audio_features(track['track']['uri'])[0]
        except:
            print("An exception occurred while processing the song: " + track['track']['name'])

    # Convert to DataFrames
    ref_df = pd.DataFrame(ref_analysis).T
    compare_df = pd.DataFrame(compare_analysis).T
    
    # Remove unnecessary columns
    columns_to_remove = ['type', 'id', 'uri', 'track_href', 'analysis_url', 'duration_ms', 'time_signature']
    ref_df = ref_df.drop(columns=columns_to_remove)
    compare_df = compare_df.drop(columns=columns_to_remove)
    
    # Find most similar songs
    similar_songs = find_most_similar_songs(ref_df, compare_df, n_similar=10, method='cosine')
    
    # Print results
    print("Most similar songs between the two playlists:")
    for ref_idx, comp_idx, similarity in similar_songs:
        ref_song = ref_df.index[ref_idx]
        comp_song = compare_df.index[comp_idx]
        print(f"'{ref_song}' is similar to '{comp_song}' (similarity: {similarity:.4f})")