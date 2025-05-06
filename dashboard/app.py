import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output
import subprocess
import os

# === Load CSVs ===
def load_data():
    # Get the absolute path to the dashboard folder
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct full paths to CSV files
    RECENT_PATH = os.path.join(BASE_DIR, "..", "data", "recentTracks.csv")
    TOP_PATH = os.path.join(BASE_DIR, "..", "data", "toptracks.csv")

# Load data with fallback in case of error
    try:
        recent_df = pd.read_csv(RECENT_PATH)
    except FileNotFoundError:
        print("⚠️ recentTracks.csv not found!")
        recent_df = pd.DataFrame()

    try:
        top_df = pd.read_csv(TOP_PATH)
    except FileNotFoundError:
        print("⚠️ toptracks.csv not found!")
        top_df = pd.DataFrame()
    return recent_df, top_df

def preprocess(df):
    if 'played_at' in df.columns:
        df['played_at'] = pd.to_datetime(df['played_at'], errors='coerce')
        df['weekday'] = df['played_at'].dt.day_name()
        df['hour'] = df['played_at'].dt.hour
    elif 'added_at' in df.columns:
        df['added_at'] = pd.to_datetime(df['added_at'], errors='coerce')
        df['weekday'] = df['added_at'].dt.day_name()
        df['hour'] = df['added_at'].dt.hour
    else:
        df['weekday'] = 'Unknown'
        df['hour'] = -1

    def ms_to_min(ms):
        m = ms // 60000
        s = (ms % 60000) // 1000
        return float(f"{m}.{str(s).zfill(2)}")

    df['dur_min'] = df['duration_ms'].apply(ms_to_min)
    df = df[df['genre'].str.lower() != "unknown"].copy()
    df['release_year'] = df['release_year'].fillna(0).astype(int)
    return df

# === Setup App ===
app = dash.Dash(__name__)
app.title = "Spotify Dashboard"

# === App Layout ===
app.layout = html.Div([
    html.H1("🎧 Spotify Listening Dashboard - Aslı", style={'textAlign': 'center'}),

    html.Button("🔄 Reload Recent Tracks", id='reload-button', n_clicks=0),

    html.Div(id='total-time', style={'margin': '20px', 'fontWeight': 'bold'}),

    html.H2("🎼 Top Genres Comparison"),
    dcc.Graph(id='genre-comparison'),

    html.H2("📊 Genre Distribution (Top Tracks)"),
    dcc.Graph(id='genre-pie'),

    html.H2("🕒 Hourly Listening Activity (Recent)"),
    dcc.Graph(id='hour-activity'),

    html.H2("📅 Listening by Day of Week"),
    dcc.Graph(id='weekdays'),

    html.H2("📆 Release Year Distribution"),
    dcc.Graph(id='release-recent'),
    dcc.Graph(id='release-top'),

    html.H2("🎵 Track Duration Distribution (Recent)"),
    dcc.Graph(id='duration-dist'),
])

# === Callback to reload data and update graphs ===
@app.callback(
    [
        Output('genre-comparison', 'figure'),
        Output('genre-pie', 'figure'),
        Output('hour-activity', 'figure'),
        Output('weekdays', 'figure'),
        Output('release-recent', 'figure'),
        Output('release-top', 'figure'),
        Output('duration-dist', 'figure'),
        Output('total-time', 'children')
    ],
    [Input('reload-button', 'n_clicks')]
)
def update_dashboard(n_clicks):
    # OPTIONAL: trigger recent data fetch script (if working)
    # subprocess.run(["python", "../fetch_data/fetch_recent.py"])

    recent_df, top_df = load_data()
    recent_df = preprocess(recent_df)
    top_df = preprocess(top_df)

    # 1. Genre comparison
    recent_genres = recent_df['genre'].value_counts(normalize=True).head(10)
    top_genres = top_df['genre'].value_counts(normalize=True)

# Ensure both series have the same index set
    all_genres = list(set(recent_genres.index).union(set(top_genres.index)))

    genre_counts = pd.DataFrame({
    'Genre': all_genres,
    'Recent': [recent_genres.get(g, 0) for g in all_genres],
    'Top': [top_genres.get(g, 0) for g in all_genres]
    })

    genre_fig = px.bar(genre_counts.melt(id_vars='Genre'),
                       x='Genre', y='value', color='variable',
                       barmode='group', title="Recent vs Top Genre Ratios")

    # 2. Genre Pie
    genre_counts = top_df['genre'].value_counts().head(10).reset_index()
    genre_counts.columns = ['genre', 'count']

    pie_fig = px.pie(genre_counts,
                 names='genre', values='count',
                 title="Top Genres (Pie Chart)")    

    # 3. Hourly Histogram
    hour_fig = px.histogram(recent_df, x='hour', nbins=24, title="Recent Listening by Hour")

    # 4. Weekday Activity
    week_fig = px.histogram(top_df, x='weekday',
                            category_orders={"weekday": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
                            title="Top Listening Days")

    # 5. Release Year Histograms
    rel_recent = px.histogram(recent_df, x='release_year', nbins=20, title="Release Years (Recent)")
    rel_top = px.histogram(top_df, x='release_year', nbins=20, title="Release Years (Top)")

    # 6. Duration Distribution
    dur_fig = px.histogram(recent_df, x='dur_min', nbins=30, title="Track Duration (min.sec) - Recent")

    # 7. Total listening time
    total_mins = int(recent_df['duration_ms'].sum() // 60000)
    total_text = f"🕰️ Total Listening Time (Recent): {total_mins} minutes"

    return genre_fig, pie_fig, hour_fig, week_fig, rel_recent, rel_top, dur_fig, total_text

# === Run ===
if __name__ == "__main__":
    app.run(debug=True)
    