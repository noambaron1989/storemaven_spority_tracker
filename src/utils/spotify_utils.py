import logging

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from src import constants


class SpotifyClient:
    def __init__(self, logger):
        self.logger = logger
        self.logger.info('connecting to spotify client...')
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=constants.sp_client_id,
                                                                        client_secret=constants.sp_client_secret))

        self.supported_categories = None
        self.get_supported_categories()

    def get_category_playlists(self, category_id):

        self.logger.info('getting spotify top playlists from category id %s', category_id)
        to_return = {}

        limit = constants.sp_limit
        offset = 0
        while constants.sp_max_limit <= limit:
            res = self.sp.category_playlists(category_id=category_id,
                                             limit=constants.sp_max_limit,
                                             offset=offset)
            playlists = dict(map(lambda x: (x['id'], x['name']), res['playlists']['items']))
            to_return.update(playlists)

            if len(res) < constants.sp_max_limit:
                break

            offset += constants.sp_max_limit
            limit -= constants.sp_max_limit

        self.logger.info('found %s playlists for category id %s',len(to_return), category_id)
        return to_return

    def get_playlist_tracks(self, playlist_id):

        self.logger.info('getting spotify top records from playlist id %s', playlist_id)
        to_return = []

        limit = constants.sp_limit
        offset = 0
        while constants.sp_max_limit <= limit:
            res = self.sp.playlist_items(playlist_id=playlist_id, limit=constants.sp_limit)
            tracks = list(map(lambda x: x['track'], res['items']))
            to_return.extend(tracks)

            if len(res) < constants.sp_max_limit:
                break

            offset += constants.sp_max_limit
            limit -= constants.sp_max_limit

        self.logger.info('found %s records for playlist id %s',len(to_return), playlist_id)
        return to_return

    def get_supported_categories(self):
        cats = self.sp.categories(country=constants.sp_country)
        cats_dict = dict(map(lambda x: (x['name'], x['id']), cats['categories']['items']))

        self.logger.info('spotify current supported categories are: %s', cats_dict.keys())
        self.supported_categories = cats_dict


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
    _logger = logging.getLogger(__name__)

    sp = SpotifyClient(_logger)
    res1 = sp.get_category_playlists('workout')
    res2 = sp.get_playlist_tracks('37i9dQZF1DX76Wlfdnj7AP')
    print(res2)
