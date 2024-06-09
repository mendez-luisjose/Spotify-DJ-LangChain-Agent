SYSTEM_MESSAGE = """
You are JJ, an AI music-player assistant, designed to provide a personalized and engaging listening experience through thoughtful interaction and intelligent tool usage.

Your Main Responsibilities:

1. **Play Music:** Utilize your specialized toolkit to fulfill music requests.

2. **Mood Monitoring:** Constantly gauge the user's mood and adapt the music accordingly. For example, if the mood shifts from 'Happy' to 'more upbeat,' select 'Energetic' music. 

3. **Track and Artist Memory:** Be prepared to recall tracks and/or artists that the user has previously requested.

4. **Provide Guidance:** If the user appears indecisive or unsure about their selection, proactively offer suggestions based on their previous preferences or popular choices within the desired mood or genre.

5. **Seek Clarification:** If a user's request is ambiguous, don't hesitate to ask for more details.
"""

GENRE_LIST = [
    'acoustic', 'afrobeat', 'alt-rock', 'alternative', 'ambient', 'anime', 
    'black-metal', 'bluegrass', 'blues', 'bossanova', 'brazil', 'breakbeat', 
    'british', 'cantopop', 'chicago-house', 'children', 'chill', 'classical', 
    'club', 'comedy', 'country', 'dance', 'dancehall', 'death-metal', 
    'deep-house', 'detroit-techno', 'disco', 'disney', 'drum-and-bass', 'dub', 
    'dubstep', 'edm', 'electro', 'electronic', 'emo', 'folk', 'forro', 'french', 
    'funk', 'garage', 'german', 'gospel', 'goth', 'grindcore', 'groove', 
    'grunge', 'guitar', 'happy', 'hard-rock', 'hardcore', 'hardstyle', 
    'heavy-metal', 'hip-hop', 'holidays', 'honky-tonk', 'house', 'idm', 
    'indian', 'indie', 'indie-pop', 'industrial', 'iranian', 'j-dance', 
    'j-idol', 'j-pop', 'j-rock', 'jazz', 'k-pop', 'kids', 'latin', 'latino', 
    'malay', 'mandopop', 'metal', 'metal-misc', 'metalcore', 'minimal-techno', 
    'movies', 'mpb', 'new-age', 'new-release', 'opera', 'pagode', 'party', 
    'philippines-opm', 'piano', 'pop', 'pop-film', 'post-dubstep', 'power-pop', 
    'progressive-house', 'psych-rock', 'punk', 'punk-rock', 'r-n-b', 
    'rainy-day', 'reggae', 'reggaeton', 'road-trip', 'rock', 'rock-n-roll', 
    'rockabilly', 'romance', 'sad', 'salsa', 'samba', 'sertanejo', 'show-tunes', 
    'singer-songwriter', 'ska', 'sleep', 'songwriter', 'soul', 'soundtracks', 
    'spanish', 'study', 'summer', 'swedish', 'synth-pop', 'tango', 'techno', 
    'trance', 'trip-hop', 'turkish', 'work-out', 'world-music'
]

JJ_MESSAGE = """
Welcome! I am JJ, your AI DJ, Tell me your **mood** to help me select the best music for you.

#### 💿 Standard 💿 
- **Specific Song:** Play Passionfruit 
- **Controls:** Queue, Pause, Resume, Skip
- **More Info:** Explain this song 
- **Album:** Play the album from Barbie
- **Playlist:** Play my Shower playlist

#### 💿 Mood-Based 💿 
- **Genre:** I'm happy, play country 
- **Artist:** Play Migos hype songs
- **Recommendations:** I love Drake and house, recommend songs
- **Create Playlist:** Make a relaxing playlist of SZA-like songs
"""