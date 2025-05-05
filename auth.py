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

sp=spotipy.Spotify(auth_manager=SpotifyOAuth(
                   client_id=CLIENT_ID,
                   client_secret=CLIENT_SECRET,
                   redirect_uri=REDIRECT_URI,
                   scope="user-top-read user-read-recently-played"))

print(sp.me()['display_name'])  # Should print your Spotify username
features = sp.audio_features('11dFghVXANMlKmJXsNCbNl')[0]
print(features)
