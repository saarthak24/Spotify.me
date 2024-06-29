from flask import Flask, request, redirect, url_for, session, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from secret import *

app = Flask(__name__)
app.config['SESSION_COOKIE_NAME'] = 'SpotipyCookie'

scope = "user-library-read playlist-read-private playlist-modify-public playlist-modify-private"

# Configure Spotipy with Spotify app credentials
sp = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,  # Replace with your client ID
    client_secret=SPOTIPY_CLIENT_SECRET,  # Replace with your client secret
    redirect_uri=SPOTIPY_CALLBACK_URI,
    scope=scope
)

@app.route('/')
def index():
    if 'token_info' in session:
        token_info = session.get('token_info')
        sp = Spotify(auth=token_info['access_token'])
        results = sp.current_user_playlists()
        return render_template('index.html', playlists=results['items'])
    else:
        return redirect(url_for('login'))

@app.route('/login')
def login():
    auth_url = sp.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    session.clear()
    code = request.args.get('code')
    token_info = sp.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
