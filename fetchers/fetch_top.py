import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd

# === STEP 1: Load credentials ===
load_dotenv()
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

# === STEP 2: Authenticate ===
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-top-read",
    cache_path=".cache"
))

# === STEP 3: Fetch top tracks ===
top_tracks = sp.current_user_top_tracks(limit=50, time_range='medium_term')

track_data = []

for item in top_tracks['items']:
    track_name = item['name']
    artist_name = item['artists'][0]['name']
    artist_id = item['artists'][0]['id']
    track_id = item['id']
    popularity = item['popularity']
    duration_ms = item['duration_ms']
    release_date = item['album']['release_date']

    # === NEW: Fetch genre from artist endpoint ===
    try:
        artist_info = sp.artist(artist_id)
        genre = artist_info['genres'][0] if artist_info['genres'] else "unknown"
    except:
        genre = "unknown"

    release_year = int(release_date[:4]) if release_date else 0

    track_data.append({
        'track_name': track_name,
        'artist_name': artist_name,
        'artist_id': artist_id,
        'track_id': track_id,
        'popularity': popularity,
        'duration_ms': duration_ms,
        'release_date': release_date,
        'release_year': release_year,
        'genre': genre  # ✅ Added genre
    })

# === STEP 4: Save to CSV ===
df = pd.DataFrame(track_data)
os.makedirs("data", exist_ok=True)
df.to_csv("data/toptracks.csv", index=False)
print("✅ Top tracks with genre saved to data/toptracks.csv")
