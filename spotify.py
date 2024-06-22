import os
import traceback
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from requests.exceptions import Timeout
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import lyricsgenius
import requests
from bs4 import BeautifulSoup
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage
from prompts import GENRE_LIST
from fuzzywuzzy import fuzz
import random
import streamlit as st
import base64
from utils import text_to_speech
import time
import streamlit as st


# Spotify configs
client_id = st.secrets["SPOTIFY_CLIENT_ID"]
client_secret = st.secrets["SPOTIFY_CLIENT_SECRET"]
redirect_uri = st.secrets["SPOTIFY_REDIRECT_URL"]
GENIUS_TOKEN = st.secrets["GENIUS_TOKEN"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

#scope = ['playlist-modify-public', 'user-modify-playback-state']
scope = [
    'user-library-read',
    'user-read-playback-state',
    'user-modify-playback-state',
    'playlist-modify-public',
    'user-top-read'
]

MOOD_LIST = ["happy", "sad", "energetic", "calm"]
# adjectives for playlist names
THEMES = ["Epic", "Hypnotic", "Dreamy", "Legendary", "Majestic", 
          "Enchanting", "Ethereal", "Super Lit", "Harmonious", "Heroic"]
MOOD_SETTINGS = {
    "happy": {"max_instrumentalness": 0.001, "min_valence": 0.6},
    "sad": {"max_danceability": 0.65, "max_valence": 0.4},
    "energetic": {"min_tempo": 120, "min_danceability": 0.75},
    "calm": {"max_energy": 0.65, "max_tempo": 130}
}

# genre + mood function
NUM_ARTISTS = 20 # artists to retrieve from user's top artists
TIME_RANGE = "medium_term" # short, medium, long
NUM_TRACKS = 10 # tracks to add to playback
MAX_ARTISTS = 4 # sp.recommendations() seeds: 4/5 artists, 1/5 genre

# artist + mood function
NUM_ALBUMS = 20 # maximum number of albums to retrieve from an artist
MAX_TRACKS = 10 # tracks to randomly select from an artist

MODEL = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2') # smaller BERT
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0, google_api_key=GOOGLE_API_KEY, convert_system_message_to_human=True)

sp = st.session_state.sp

MOOD_EMBEDDINGS = MODEL.encode(MOOD_LIST)
GENRE_EMBEDDINGS = MODEL.encode(GENRE_LIST) 


#MODEL = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2') # smaller BERT
#llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0, google_api_key=GOOGLE_API_KEY, convert_system_message_to_human=True)

#sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
#                     client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

#sp = spotipy.Spotify(auth=st.secrets["SPOTIFY_TOKEN"])
#MOOD_EMBEDDINGS = MODEL.encode(MOOD_LIST)
#GENRE_EMBEDDINGS = MODEL.encode(GENRE_LIST) 

#devices = sp.devices()
#device_id = devices['devices'][0]['id']

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    md = f"""
    <audio autoplay>
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

def find_song_by_name(name: str):
    """
    Finds the Spotify track URI given the track name.
    """
    results = sp.search(q=name, type='track')
    if (results):
        song_uri = results['tracks']['items'][0]['uri']
        return song_uri
    
def start_playing_song_by_name(song_name: str):
    """
    Plays a track given its name. Uses the above function.
    """
    try:
        song_uri = find_song_by_name(song_name)
        track_name = sp.track(song_uri)["name"]
        artist_name = sp.track(song_uri)['artists'][0]['name']
        if (song_uri):
            file_path = text_to_speech(f"Now playing {track_name} by {artist_name}")
            autoplay_audio(file_path)
            time.sleep(3)
            sp.start_playback(uris=[song_uri])
            return f"♫ Now playing **{track_name}** by **{artist_name}** ♫"
    except SpotifyException as e:
        return f"An error occurred with Spotify: {e}. \n\n**Remember to wake up Spotify.**"
    except Exception as e:
        error_message = traceback.format_exc()  # Get the formatted error message
        return f"Couldn't play song. Error: {error_message}"

# Spotify functions
def add_song_to_queue(song_uri: str, track_name:str):
    try:
        sp.add_to_queue(song_uri)
        return f"♫ Added {track_name} to your queue ♫"
    except:
        return "Error adding track to queue"
    
def add_song_to_queue_by_song_name(song_name: str):
    song_uri = find_song_by_name(song_name)
    if (song_uri):
        track_name = sp.track(song_uri)["name"]
        add_song_to_queue(song_uri, track_name)
        return f"♫ Added **{track_name}** to your queue ♫"
    else:
        return "No matching tracks found"


def find_song_by_lyrics(lyrics: str):
    results = sp.search(q=f"lyrics:{lyrics}", type='track')
    if (results):
        if len(results['tracks']['items']) > 0:
            song_uri = results['tracks']['items'][0]['uri']
            return song_uri
        else:
            return ("No matching tracks found")


def add_song_to_queue_by_lyrics(lyrics: str):
    song_uri = find_song_by_lyrics(lyrics)
    if (song_uri):
        return add_song_to_queue(song_uri)
    else:
        return "No matching tracks found"

def start_playing_song_by_lyrics(lyrics: str):
    song_uri = find_song_by_lyrics(lyrics)
    if (song_uri):
        sp.start_playback(uris=[song_uri])
        return f"Started playing song with lyrics: **{lyrics}**"
    else:
        return "No matching tracks found"


def start_playlist_by_artist_name(playlist_name: str):
    """This defaults to playing the current user's playlist"""
    results = sp.search(q=playlist_name, type="playlist", limit=1)

    if results and results["playlists"]["items"]:
        playlist_uri = results["playlists"]["items"][0]["uri"]
        sp.start_playback(context_uri=playlist_uri)
        return ("Playlist started:", playlist_name)
    else:
        return ("Playlist not found.")
    
def play_playlist_from_user(playlist_name):
    """
    Plays an existing playlist in the user's library given its name.
    """
    try: 
        playlists = sp.current_user_playlists()
        playlist_dict = {playlist['name']: (playlist['id'], playlist['owner']['display_name']) for playlist in playlists['items']}
        playlist_names = [key for key in playlist_dict.keys()]

        # defined inside to capture user-specific playlists
        playlist_name_embeddings = MODEL.encode(playlist_names)
        user_playlist_embedding = MODEL.encode([playlist_name])

        # compares (embedded) given name to (embedded) playlist library and outputs the closest match
        similarity_scores = cosine_similarity(user_playlist_embedding, playlist_name_embeddings)
        most_similar_index = similarity_scores.argmax()
        playlist_name = playlist_names[most_similar_index]
        playlist_id, creator_name = playlist_dict[playlist_name]
        file_path = text_to_speech(f"Now playing {playlist_name} Playlist by {creator_name}")
        autoplay_audio(file_path)
        time.sleep(3)
        sp.start_playback(context_uri=f'spotify:playlist:{playlist_id}')
        return f'♫ Now playing **{playlist_name}** Playlist by **{creator_name}** ♫'
    except: 
        return "Unable to find playlist. Please try again."
    
def play_song_by_name_and_artist(song_name, artist_name):
    """
    Plays a song given its name and the artist.
    context_uri (provide a context_uri to start playback of an album, artist, or playlist) expects a string.
    """  
    try: 
        results = sp.search(q=f'{song_name} {artist_name}', type='track')
        song_uri = results['tracks']['items'][0]['uri']
        if (song_uri) :
            track_name = sp.track(song_uri)["name"]
            artist_name = sp.track(song_uri)['artists'][0]['name']
            file_path = text_to_speech(f"Now playing {track_name} by {artist_name}")
            autoplay_audio(file_path)
            time.sleep(3)
            sp.start_playback(uris=[song_uri])
            return f"♫ Now playing **{track_name}** by **{artist_name}** ♫"
    except spotipy.SpotifyException as e:
        return f"An error occurred with Spotify: {e}. \n\n**Remember to wake up Spotify.**"
    except Timeout:
        return f"An unexpected error occurred: {e}."
    
def play_album_by_name_and_artist(album_name, artist_name):
    """
    Plays an album given its name and the artist.
    context_uri (provide a context_uri to start playback of an album, artist, or playlist) expects a string.
    """  
    try: 
        results = sp.search(q=f'{album_name} {artist_name}', type='album')
        album_id = results['albums']['items'][0]['id']
        album_info = sp.album(album_id)
        album_name = album_info['name']
        artist_name = album_info['artists'][0]['name']
        file_path = text_to_speech(f"Now playing {album_name} by {artist_name}")
        autoplay_audio(file_path)
        time.sleep(3)
        sp.start_playback(context_uri=f'spotify:album:{album_id}')
        return f"♫ Now playing **{album_name}** by **{artist_name}** ♫"
    except spotipy.SpotifyException as e:
        return f"An error occurred with Spotify: {e}. \n\n**Remember to wake up Spotify.**"
    except Timeout:
        return f"An unexpected error occurred: {e}."
    
def get_track_info(): 
    """
    Harvests information for explain_track() using Genius' API and basic webscraping. 
    """
    current_track_item = sp.current_user_playing_track()['item']
    track_name = current_track_item['name']
    artist_name = current_track_item['artists'][0]['name']
    album_name = current_track_item['album']['name']
    release_date = current_track_item['album']['release_date']
    basic_info = {
        'track_name': track_name,
        'artist_name': artist_name,
        'album_name': album_name,
        'release_date': release_date,
    }

    # define inside to avoid user conflicts (simultaneously query Genius)
    genius = lyricsgenius.Genius(GENIUS_TOKEN)
    # removing feature information from song titles to avoid scewing search
    track_name = re.split(' \(with | \(feat\. ', track_name)[0]
    result = genius.search_song(track_name, artist_name)

    # if no Genius page exists
    if result is not None and hasattr(result, 'artist'):
        genius_artist = result.artist.lower().replace(" ", "")
        spotify_artist = artist_name.lower().replace(" ", "")
        #debug_print(spotify_artist)
        #debug_print(genius_artist)
        if spotify_artist not in genius_artist:
            return basic_info, None, None, None
    else: 
        genius_artist = None
        return basic_info, None, None, None
    
    # if Genius page exists
    lyrics = result.lyrics
    url = result.url
    response = requests.get(url)

    # parsing the webpage and locating 'About' section
    soup = BeautifulSoup(response.text, 'html.parser')
    # universal 'About' section element across all Genius song lyrics pages
    about_section = soup.select_one('div[class^="RichText__Container-oz284w-0"]')

    # if no 'About' section exists
    if not about_section: 
        return basic_info, None, lyrics, url
    
    # if 'About' section exists
    else: 
        about_section = about_section.get_text(separator='\n')
        return basic_info, about_section, lyrics, url


def explain_track(): 
    """
    Displays track information in an organized, informational, and compelling manner. 
    Uses the above function.
    """
    basic_info, about_section, lyrics, url = get_track_info()
    #debug_print(basic_info, about_section, lyrics, url)

    if lyrics: # if Genius page exists
        system_message_content = """
            Your task is to create an engaging summary for a track using the available details
            about the track and its lyrics. If there's insufficient or no additional information
            besides the lyrics, craft the entire summary based solely on the lyrical content."
            """
        human_message_content = f"{about_section}\n\n{lyrics}"
        messages = [
            SystemMessage(content=system_message_content),
            HumanMessage(content=human_message_content)
        ]
        ai_response = llm(messages).content
        summary = f"""
            **Name:** {basic_info["track_name"]} 
            **Artist:** {basic_info["artist_name"]} 
            **Album:** {basic_info["album_name"]}  
            **Release:** {basic_info["release_date"]}   
            
            **About:** 
            {ai_response}
        """
        return summary
    
    else: # if no Genius page exists
        url = "https://genius.com/Genius-how-to-add-songs-to-genius-annotated"
        summary = f"""
            **Name:**{basic_info["track_name"]} 
            **Artist:** {basic_info["artist_name"]}    
            **Album:** {basic_info["album_name"]}  
            **Release:** {basic_info["release_date"]}   
            
            **About:** 
            Unfortunately, this track has not been uploaded to Genius.com
        """
        return summary
    
def get_user_mood(user_mood):
    """
    Categorizes the user's mood as either 'happy', 'sad', 'energetic', or 'calm'.
    Uses same cosine similarity/embedding concepts as with determining playlist names.
    """
    if user_mood.lower() in MOOD_LIST:
        user_mood = user_mood.lower()
        return user_mood
    else:
        user_mood_embedding = MODEL.encode([user_mood.lower()])
        similarity_scores = cosine_similarity(user_mood_embedding, MOOD_EMBEDDINGS)
        most_similar_index = similarity_scores.argmax()
        user_mood = MOOD_LIST[most_similar_index]
        return user_mood
    
def get_genre_by_name(genre_name): 
    """
    Matches user's desired genre to closest (most similar) existing genre in the list of genres.
    recommendations() only accepts genres from this list.
    """
    if genre_name.lower() in GENRE_LIST:
        genre_name = genre_name.lower()
        return genre_name
    else:
        genre_name_embedding = MODEL.encode([genre_name.lower()])
        similarity_scores = cosine_similarity(genre_name_embedding, GENRE_EMBEDDINGS)
        most_similar_index = similarity_scores.argmax()
        genre_name = GENRE_LIST[most_similar_index]
        return genre_name
    
def is_genre_match(genre1, genre2, threshold=75):
    """
    Determines if two genres are semantically similar.
    token_set_ratio() - for quantifying semantic similarity - and 
    threshold of 75 (out of 100) were were arbitrarily determined through basic testing.
    """
    score = fuzz.token_set_ratio(genre1, genre2)
    #debug_print(score) 
    return score >= threshold

def create_track_list_str(track_uris):
    """
    Creates an organized list of track names. 
    Used in final return statements by functions below.
    """
    track_details = sp.tracks(track_uris)
    track_names_with_artists = [f"{track['name']} by {track['artists'][0]['name']}" for track in track_details['tracks']]
    track_list_str = " - ".join(track_names_with_artists) 
    return track_list_str

def play_genre_by_name_and_mood(genre_name, user_mood):
    """
    1. Retrieves user's desired genre and current mood.
    2. Matches genre and mood to existing options.
    3. Gets 4 of user's top artists that align with genre.
    4. Conducts personalized recommendations() search.
    5. Plays selected track, clears the queue, and adds the rest to the now-empty queue.
    """

    if type(user_mood) != str or user_mood == None : 
        user_mood = "unknown"

    if type(genre_name) != str or genre_name == None : 
        genre_name = "pop"

    genre_name = get_genre_by_name(genre_name)
    user_mood = get_user_mood(user_mood).lower()
    #debug_print(genre_name) 
    #debug_print(user_mood)
    
    # increased personalization
    user_top_artists = sp.current_user_top_artists(limit=NUM_ARTISTS, time_range=TIME_RANGE) 
    matching_artists_ids = []

    for artist in user_top_artists['items']:
        #debug_print(artist['genres']) 
        for artist_genre in artist['genres']:
            if is_genre_match(genre_name, artist_genre):
                matching_artists_ids.append(artist['id'])
                break # don't waste time cycling artist genres after match
        if len(matching_artists_ids) == MAX_ARTISTS:
            break 

    if not matching_artists_ids:
        matching_artists_ids = None
    else: 
        artist_names = [artist['name'] for artist in sp.artists(matching_artists_ids)['artists']]
        #debug_print(artist_names)
        #debug_print(matching_artists_ids)

    recommendations = sp.recommendations( # accepts maximum {genre + artists} = 5 seeds
                                    seed_artists=matching_artists_ids, 
                                    seed_genres=[genre_name], 
                                    seed_tracks=None, 
                                    limit=NUM_TRACKS, # number of tracks to return
                                    country=None,
                                    **MOOD_SETTINGS[user_mood]) # maps to mood settings dictionary
                                    
    track_uris = [track['uri'] for track in recommendations['tracks']]
    track_list_str = create_track_list_str(track_uris)
    
    file_path = text_to_speech(f"Now playing {genre_name}")
    autoplay_audio(file_path)
    time.sleep(3)
    sp.start_playback(uris=track_uris)

    return f"""
    **♫ Now Playing:** {genre_name} ♫

    **Selected Tracks**: {track_list_str}
    """

def play_artist_by_name_and_mood(artist_name, user_mood):
    """
    Plays tracks (randomly selected) by a given artist that matches the user's mood.
    """
    if type(user_mood) != str or user_mood == None : 
        user_mood = "unknown"

    user_mood = get_user_mood(user_mood).lower()
    #debug_print(user_mood)

    # retrieving and shuffling all artist's tracks
    first_name = artist_name.split(',')[0].strip()
    results = sp.search(q=first_name, type='artist')
    artist_id = results['artists']['items'][0]['id']
    # most recent albums retrieved first
    artist_albums = sp.artist_albums(artist_id, album_type='album', limit=NUM_ALBUMS)
    artist_tracks = []
    for album in artist_albums['items']:
        album_tracks = sp.album_tracks(album['id'])['items']
        artist_tracks.extend(album_tracks)
    random.shuffle(artist_tracks) 

    # filtering until we find enough (MAX_TRACKS) tracks that match user's mood
    selected_tracks = []
    for track in artist_tracks:
        if len(selected_tracks) == MAX_TRACKS: 
            break
        features = sp.audio_features([track['id']])[0]
        mood_criteria = MOOD_SETTINGS[user_mood]

        match = True
        for criteria, threshold in mood_criteria.items():
            if "min_" in criteria and features[criteria[4:]] < threshold:
                match = False
                break
            elif "max_" in criteria and features[criteria[4:]] > threshold:
                match = False
                break
        if match:
            #debug_print(f"{features}\n{mood_criteria}\n\n") 
            selected_tracks.append(track)

    track_names = [track['name'] for track in selected_tracks]
    track_list_str = " - ".join(track_names)  # using HTML line breaks for each track name
    #debug_print(track_list_str)
    track_uris = [track['uri'] for track in selected_tracks]
    
    file_path = text_to_speech(f"Now playing {artist_name}")
    autoplay_audio(file_path)
    time.sleep(3)
    sp.start_playback(uris=track_uris)

    return f"""
    **♫ Now Playing:** {artist_name} ♫ 

    **Selected Tracks**: {track_list_str}
    """

def recommend_tracks(genre_name=None, artist_name=None, track_name=None, user_mood=None):
    """
    1. Retrieves user's preferences based on artist_name, track_name, genre_name, and/or user_mood.
    2. Uses these parameters to conduct personalized recommendations() search.
    3. Returns the track URIs of (NUM_TRACKS) recommendation tracks.
    """

    user_mood = get_user_mood(user_mood).lower() if user_mood else None
    #debug_print(user_mood)

    seed_genre, seed_artist, seed_track = None, None, None

    if genre_name:
        first_name = genre_name.split(',')[0].strip() 
        genre_name = get_genre_by_name(first_name)
        seed_genre = [genre_name]
        #debug_print(seed_genre)

    if artist_name:
        first_name = artist_name.split(',')[0].strip() # if user provides multiple artists, use the first
        results = sp.search(q='artist:' + first_name, type='artist')
        seed_artist = [results['artists']['items'][0]['id']]

    if track_name:
        first_name = track_name.split(',')[0].strip()
        results = sp.search(q='track:' + first_name, type='track')
        seed_track = [results['tracks']['items'][0]['id']]
    
    # if user requests recommendations without specifying anything but their mood
    # this is because recommendations() requires at least one seed
    if seed_genre is None and seed_artist is None and seed_track is None:
        raise ValueError("At least one genre, artist, or track must be provided.")
    
    recommendations = sp.recommendations( # passing in 3 seeds
                            seed_artists=seed_artist, 
                            seed_genres=seed_genre, 
                            seed_tracks=seed_track, 
                            limit=NUM_TRACKS,
                            country=None,
                            **MOOD_SETTINGS[user_mood] if user_mood else {})
    
    track_uris = [track['uri'] for track in recommendations['tracks']]
    return track_uris

def play_recommended_tracks(genre_name=None, artist_name=None, track_name=None, user_mood=None):
    """
    Plays the track_uris returned by recommend_tracks().
    """
    try:
        if type(user_mood) != str : 
            user_mood = "unknown"
        track_uris = recommend_tracks(genre_name, artist_name, track_name, user_mood)
        track_list_str = create_track_list_str(track_uris) 
        
        file_path = text_to_speech(f"Here are some songs recommendations")
        autoplay_audio(file_path)
        time.sleep(3)
        sp.start_playback(uris=track_uris)

        return f"""
        **♫ Now Playing Recommendations Based On:** 
        {', '.join(filter(None, [genre_name, artist_name, track_name, "Your Mood"]))} ♫

        **Selected Tracks:** {track_list_str}
        """
    except spotipy.client.SpotifyException as e:
        return ("Error in the Spotify Client - Try Again:", e)
    except ValueError as e:
        return str(e)  
    
def create_playlist_from_recommendations(genre_name=None, artist_name=None, track_name=None, user_mood=None):
    """
    Creates a playlist from recommend_tracks(). 
    """
    user = sp.current_user()
    user_id = user['id']
    user_name = user["display_name"]

    playlists = sp.current_user_playlists()
    playlist_names = [playlist['name'] for playlist in playlists["items"]]
    chosen_theme = random.choice(THEMES)
    playlist_name = f"{user_name}'s {chosen_theme} Playlist"
    # ensuring the use of new adjective each time
    while playlist_name in playlist_names:
        chosen_theme = random.choice(THEMES)
        playlist_name = f"{user_name}'s {chosen_theme} Playlist"

    playlist_description=f"JJ AI's personalized playlist for {user_name}."
    new_playlist = sp.user_playlist_create(user=user_id, name=playlist_name, 
                                                    public=True, collaborative=False, description=playlist_description)
    
    if type(user_mood) != str : 
        user_mood = "unknown"

    track_uris = recommend_tracks(genre_name, artist_name, track_name, user_mood)
    track_list_str = create_track_list_str(track_uris) 
    sp.user_playlist_add_tracks(user=user_id, playlist_id=new_playlist['id'], tracks=track_uris, position=None)
    playlist_url = f"https://open.spotify.com/playlist/{new_playlist['id']}"

    file_path = text_to_speech(f"Here is a playlist based on your taste")
    autoplay_audio(file_path)
    time.sleep(3)

    return f"""
    ♫ Created *{playlist_name}* Based On:
    {', '.join(filter(None, [genre_name, artist_name, track_name, 'Your Mood']))} ♫

    **Selected Tracks:** {track_list_str}

    URL to the playlist on Spotify! -> {playlist_url}
    """


def start_music():
    try:
        """
        Resumes the current playback.
        """
        if (sp.currently_playing()["is_playing"]!=True) :
            sp.start_playback()
        return "♫ Playback started! ♫"
    except spotipy.client.SpotifyException as e:
        return ("Error occurred while starting track:", e)
    except:
        return "Error starting playback. Make sure to wake the player up before starting."


def pause_music():
    try:
        """
        Pauses the current playback.
        """
        if (sp.currently_playing()["is_playing"]) :
            sp.pause_playback()
        return "♫ Playback paused ♫"
    except spotipy.client.SpotifyException as e:
        return ("Error occurred while pausing track:", e)
    except:
        return "Error pausing playback. Make sure to wake the player up before stopping."


def next_track():
    try:
        """
        Plays the next playback.
        """
        if (sp.currently_playing()["is_playing"]) :
            sp.next_track()
        return "♫ Successfully skipped to the next track ♫"
    except spotipy.client.SpotifyException as e:
        return ("Error occurred while skipping track:", e)
    except:
        return "Error. Make sure to wake the player up before stopping."


def previous_track():
    try:
        """
        Plays the previous song.
        """
        if (sp.currently_playing()["is_playing"]) :
            sp.previous_track()
        return "♫ Successfully went back to the previous track ♫"
    except Exception as e:
        error_message = traceback.format_exc()  # Get the formatted error message
        return f"Error occurred while going back to the previous track: {error_message}"
    except:
        return "Error. Make sure to wake the player up before stopping."
    
