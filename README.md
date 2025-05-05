# 🎵 Spotify Listening Dashboard

A Python app that fetches your recent Spotify listening data using the Spotipy API and exports it with audio features to a CSV file.

## Features
- Authenticates via OAuth2
- Fetches your 50 most recently played tracks
- Extracts audio features (danceability, valence, etc.)
- Adds genre, artist, weekday/hour, and seasonal info
- Saves it all to a `.csv` for analysis!

## Usage
1. Clone this repo
2. Create a `.env` file with your Spotify credentials:
