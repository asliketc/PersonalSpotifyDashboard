import os  #for environment variables
from dotenv import load_dotenv #to load values from .env file
import spotipy
from spotipy.oauth2 import SpotifyOAuth #for secure user authentication
import pandas as pd 
import json 

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
    track_id=track['id']

    #getting audio features
    try:
        features_list = sp.audio_features([track_id])
        features = features_list[0] if features_list else None
        if features is None:
            print(f"⚠️ No audio features found for track ID: {track_id}")
            continue
    except Exception as e:
        print(f"❌ Failed to get features for {track['name']} ({track_id}): {e}")
        continue
 #returns a list so we get [0]

    #artist & genre information
    artist_id=track['artists'][0]['id']
    artist_info=sp.artist(artist_id)
    genres=artist_info['genres']
    genre= genres[0] if genres else "unknown genre"
    #there can be more than one genre so takes the FIRST genre information

    track_data.append({
        'played_at':item['played_at'],
        'track_name':track['name'],
        'artist':track['artists'][0]['name'],
        'id':track['id'],
        'popularity':track['popularity'],
        'duration_ms':track['duration_ms'],
        'genre': genre,
        'danceability':features['danceability'],
        'energy':features['energy'],
        'valence':features['valence'],
        'tempo':features['tempo'],
        'acousticness':features['acousticness'],
        'speechiness':features['speechiness'],
        'loudness':features['loudness']
    })


    #to DF
df=pd.DataFrame(track_data)
df['played_at']=pd.to_datetime(df['played_at'])
df['weekday']=df['played_at'].dt.day_name()
df['hour']=df['played_at'].dt.hour
df['month_name']=df['played_at'].dt.month_name

    #season retrieval
def season_info(month):
    if month in [12,1,2]:
        return "Winter"
    elif month in [3,4,5]:
        return "Spring"
    elif month in [6,7,8]:
        return "Summer"
    elif month in [9,10,11]:
        return "Fall"
    else:
        return "Unable to detect"
        
df['season']=df['month'].apply(season_info)




#-----STEP 4: TO CSV-----
os.makedirs("data",exist_ok=True)
df.to_csv("data/features_of_recenttracks.csv",index=False)
print("Data Saved to new .csv")




