import os  #for environment variables
from dotenv import load_dotenv #to load values from .env file
import spotipy
from spotipy.oauth2 import SpotifyOAuth #for secure user authentication
import pandas as pd 
import json 
import seaborn as sns 
import matplotlib.pyplot as plt 

#-------STEP 1: Loading environmental variables------
load_dotenv()

#now access the secret credentials from .env and assign them to variables
CLIENT_ID= os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET= os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI= os.getenv("SPOTIPY_REDIRECT_URI")

#-----STEP 2: SPOTIFY AUTH MANAGER SET UP-----
#-----------------------------------------------

# SpotifyOAuth handles the 3-legged OAuth flow:
# 1. Redirects to login page
# 2. Asks user for permission
# 3. Returns access + refresh tokens

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-top-read user-read-recently-played user-library-read",
    cache_path=".cache"  #token reuse and refresh
))


#-----STEP 3: GETTING RECENT TRACKS-----
recent=sp.current_user_recently_played(limit=50) #returns JSON

#parsing the JSON that has been returned from above command
track_data=[]

for item in recent['items']:

    track=item['track']
    artist=track['artists'][0]
    artist_info=sp.artist(artist['id'])
    genre=artist_info['genres'][0] if artist_info['genres'] else "unknown"
    #there can be more than one genre so takes the FIRST genre information

    track_data.append({
        'played_at':item['played_at'],
        'track_name':track['name'],
        'artist':track['artists'][0]['name'],
        'id':track['id'],
        'popularity':track['popularity'],
        'duration_ms':track['duration_ms'],
        'genre': genre,
        'release_year':int(track['album']['release_date'][:4])
    })

#to DF
df=pd.DataFrame(track_data)
df['played_at']=pd.to_datetime(df['played_at'])
df['weekday']=df['played_at'].dt.day_name()
df['hour']=df['played_at'].dt.hour

#print(df)

#-----STEP 4: TO CSV-----
os.makedirs("data",exist_ok=True)
df.to_csv("data/recentTracks.csv",index=False)
print("Data Saved to new .csv")
