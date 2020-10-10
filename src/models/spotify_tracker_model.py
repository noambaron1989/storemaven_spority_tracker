import time

table_name = 'spotify_tracker'

key_track_id = "trackId"
key_timestamp = "timestamp"
key_category_name = "categoryName"
key_playlist_name = "playlistName"
key_playlist_index = "playlistIndex"
key_track_index = "trackIndex"
key_track_name = "trackName"
key_artist_name = "artistName"
key_popularity = "popularity"
key_danceabitlity = "danceability"
key_loudness = "loudness"

model_schema = [
    {
        "name": key_track_id,
        "type": "varchar(100)"
    }, {
        "name": key_timestamp,
        "type": "bigint"
    }, {
        "name": key_category_name,
        "type": "varchar(100)"
    }, {
        "name": key_playlist_name,
        "type": "varchar(100)"
    }, {
        "name": key_playlist_index,
        "type": "int"
    }, {
        "name": key_track_index,
        "type": "int"
    }, {
        "name": key_track_name,
        "type": "varchar(100)"
    }, {
        "name": key_artist_name,
        "type": "varchar(512)"
    }, {
        "name": key_popularity,
        "type": "int"
    }, {
        "name": key_danceabitlity,
        "type": "int"
    }, {
        "name": key_loudness,
        "type": "int"
    }
]


def create_tracker(track_id, category_name, playlist_name, playlist_ind, track_ind, track_name, artist_name, popularity,
                   danceabitlity=None, loudness=None):
    return {
        key_track_id: track_id,
        key_timestamp: int(time.time()),
        key_category_name: category_name,
        key_playlist_name: playlist_name,
        key_playlist_index: playlist_ind,
        key_track_index: track_ind,
        key_track_name: track_name,
        key_artist_name: artist_name,
        key_popularity: popularity,
        key_danceabitlity: danceabitlity,
        key_loudness: loudness
    }

def insert_tracker():
    pass