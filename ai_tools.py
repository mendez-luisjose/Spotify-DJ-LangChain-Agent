from pydantic.v1 import BaseModel, Field
from spotify import start_playing_song_by_name, start_playing_song_by_lyrics, start_music, pause_music, start_playlist_by_artist_name, next_track, previous_track, play_album_by_name_and_artist, play_song_by_name_and_artist, play_playlist_from_user, explain_track, play_genre_by_name_and_mood, play_artist_by_name_and_mood, play_recommended_tracks, create_playlist_from_recommendations
from langchain.tools import tool


class LyricsInput(BaseModel):
    lyrics: str = Field(
        description="lyrics in the user's request", default="", exclude=None)

class SongNameInput(BaseModel):
    song: str = Field(
        description="song name in the user's request", default="", exclude=None)

class PlaylistArtistNameInput(BaseModel):
    playlist: str = Field(
        description="playlist name in the user's request.", default="", exclude=None)
    
class UserPlaylistNameInput(BaseModel):
    playlist_name: str = Field(description="Playlist name in the user's request.", default="", exclude=None) 
    
class AlbumNameAndArtistNameInput(BaseModel):
    album_name: str = Field(description="Album name in the user's request.", default="", exclude=None)
    artist_name: str = Field(description="Artist name in the user's request.", default="", exclude=None) 

class SongNameAndArtistNameInput(BaseModel):
    song_name: str = Field(description="Song name in the user's request.", default="", exclude=None)
    artist_name: str = Field(description="Artist name in the user's request.", default="", exclude=None) 

class GenreNameAndUserMoodInput(BaseModel):
    genre_name: str = Field(description="Genre name in the user's request.", default="", exclude=None)
    user_mood: str = Field(description="User's current mood/state-of-being or mood name in the user's request.", default="", exclude=None) 

class ArtistNameAndUserMoodInput(BaseModel):
    artist_name: str = Field(description="Artist name in the user's request.", default="", exclude=None) 
    user_mood: str = Field(description="User's current mood/state-of-being or mood name in the user's request.", default="", exclude=None) 

class RecommendationsInput(BaseModel):
    genre_name: str = Field(description="Genre name in the user's request.", default="", exclude=None)
    artist_name: str = Field(description="Artist name in the user's request.", default="", exclude=None)
    track_name: str = Field(description="Track name in the user's request.", default="", exclude=None)
    user_mood: str = Field(description="User's current mood/state-of-being or mood name in the user's request.", default="", exclude=None) 

@tool("play_song_by_lyrics", return_direct=True, args_schema=LyricsInput)
def by_lyrics(lyrics: str) -> str:
    """
    Extract the lyrics from user's request and play the song.
    The parameter must be of type string.
    """
    return start_playing_song_by_lyrics(lyrics)


@tool("play_song_by_name", return_direct=True, args_schema=SongNameInput)
def by_name(song: str) -> str:
    """
    Extract the song name from user's request and play the song.
    The parameter must be of type string.
    """
    return start_playing_song_by_name(song)

@tool("play_song_by_name_and_artist", return_direct=True, args_schema=SongNameAndArtistNameInput) 
def tool_play_song_by_name_and_artist(song_name, artist_name) :
    """
    Use this tool when a user wants to play a song given its name and the name of the artist.
    You will need to identify both the song name and artist name from the user's request.
    Usually, the requests will look like 'play the song {song_name} by {artist_name}'. 
    All parameters must be of type string.
    """
    return play_song_by_name_and_artist(song_name, artist_name)

@tool("play_album_by_name_and_artist", return_direct=True, args_schema=AlbumNameAndArtistNameInput) 
def tool_play_album_by_name_and_artist(album_name, artist_name) :
    """
    Use this tool when a user wants to play an album.
    You will need to identify both the album name and artist name from the user's request.
    Usually, the requests will look like 'play the album {album_name} by {artist_name}'. 
    All parameters must be of type string.
    """
    return play_album_by_name_and_artist(album_name, artist_name)

@tool("explain_track", return_direct=True) 
def tool_explain_track() :
    """
    Use this tool when a user wants to know about the currently playing track.
    """
    return explain_track()


@tool("start_music", return_direct=True)
def tool_start_music() :
    """
    Use this tool when a user wants to start the song.
    """
    return start_music()


@tool("pause_music", return_direct=True)
def tool_pause_music() :
    """
    Use this tool when a user wants to pause the current track.
    """
    return pause_music()


@tool("next_track", return_direct=True)
def tool_next_track() :
    """
    Use this tool when a user wants to skip the current track or play the next song.
    """
    return next_track()


@tool("previous_track", return_direct=True)
def tool_previous_track() :
    """
    Use this tool when a user wants to play the previous song.
    """
    return previous_track()


@tool("start_playlist_by_artist_name", return_direct=True, args_schema=PlaylistArtistNameInput)
def tool_start_playlist_by_artist_name(playlist: str) -> str:
    """
    Use this tool when a user wants to play a playlist of an artist.
    You will need to identify and extract the playlist name from user's request and play the playlist.
    The parameter must be of type string.
    """
    return start_playlist_by_artist_name(playlist)

@tool("play_playlist_from_user", return_direct=True, args_schema=UserPlaylistNameInput) 
def tool_play_playlist_from_user(playlist_name: str) -> str:
    """
    Use this tool when a user wants to play one of their own playlists.
    You will need to identify the playlist name from the user's request. 
    The parameter must be of type string.
    """
    return play_playlist_from_user(playlist_name)

@tool("play_genre_by_name_and_mood", return_direct=True, args_schema=GenreNameAndUserMoodInput) 
def tool_play_genre_by_name_and_mood(genre_name, user_mood) :
    """
    Use this tool when a user wants to play a genre.
    You will need to identify both the genre name from the user's request, 
    and also their current mood, which you should always be monitoring. 
    If you don't know the user's mood, ask them before using this tool.
    All parameters must be of type string.
    """
    return play_genre_by_name_and_mood(genre_name, user_mood)

@tool("play_artist_by_name_and_mood", return_direct=True, args_schema=ArtistNameAndUserMoodInput) 
def tool_play_artist_by_name_and_mood(artist_name, user_mood) :
    """
    Use this tool when a user wants to play an artist.
    You will need to identify both the artist name from the user's request, 
    and also their current mood, which you should always be monitoring. 
    If you don't know the user's mood, ask them before using this tool.
    All parameters must be of type string.
    """
    return play_artist_by_name_and_mood(artist_name, user_mood)

@tool("play_recommended_tracks", return_direct=True, args_schema=RecommendationsInput) 
def tool_play_recommended_tracks(genre_name, artist_name, track_name, user_mood) :
    """
    Use this tool when a user wants track recommendations.
    You will need to identify the genre name, artist name, and/or track name
    from the user's request... and also their current mood, which you should always be monitoring.
    The user must provide at least genre, artist, or track.
    If you don't know the user's mood, ask them before using this tool.
    All parameters must be of type string.
    """
    return play_recommended_tracks(genre_name, artist_name, track_name, user_mood)

@tool("create_playlist_from_recommendations", return_direct=True, args_schema=RecommendationsInput) 
def tool_create_playlist_from_recommendations(genre_name, artist_name, track_name, user_mood) :
    """
    Use this tool when a user wants a playlist created (from recommended tracks).
    You will need to identify the genre name, artist name, and/or track name
    from the user's request... and also their current mood, which you should always be monitoring.
    The user must provide at least genre, artist, or track.
    If you don't know the user's mood, ask them before using this tool.
    All parameters must be of type string.
    """
    return create_playlist_from_recommendations(genre_name, artist_name, track_name, user_mood)


music_player_tools = [
    by_name,
    by_lyrics,
    tool_start_music,
    tool_pause_music,
    tool_play_song_by_name_and_artist,
    tool_play_album_by_name_and_artist,
    #tool_start_playlist_by_artist_name,
    tool_play_artist_by_name_and_mood,
    tool_play_playlist_from_user,
    tool_play_recommended_tracks,
    tool_create_playlist_from_recommendations,
    tool_play_genre_by_name_and_mood,
    tool_explain_track,
    tool_next_track,
    tool_previous_track
]