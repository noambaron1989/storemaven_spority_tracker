import datetime
import logging
import time
import codecs

from flask import Flask, request, abort

from src.models import category_manager_model, spotify_tracker_model
from src import constants
from src.utils.spotify_utils import SpotifyClient
from src.utils.db_utils import DataProvider

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None)

app = Flask(__name__)

sp_client = SpotifyClient(logger)
db_provider = DataProvider(logger)
db_provider.create_connection()


@app.route('/track', methods=['POST'])
def track():
    message = request.get_json()
    is_dry_run = message.get('isDryRun')
    if is_dry_run is None:
        is_dry_run = False

    num_of_records = 0

    categories_to_track = db_provider.get_records_from_table(table_name=category_manager_model.table_name)
    logger.info('trying to track %s categories...', len(categories_to_track))
    for curr_category in categories_to_track:
        track_date = curr_category[category_manager_model.key_track_date]

        if track_date is None:
            num_of_records = do_category_tracking(curr_category, is_dry_run)
        else:
            track_date_dt_obj = datetime.datetime.fromtimestamp(track_date)
            if (datetime.datetime.now() - track_date_dt_obj).days == 0:
                logger.info('track was already triggered today on category %s! Not tacking.',
                            curr_category[category_manager_model.key_category_name])
            else:
                num_of_records = do_category_tracking(curr_category, is_dry_run)

    return {'numOfEffectedRecords': num_of_records}


@app.route('/entity/create', methods=['POST'])
def entity_create():
    message = request.get_json()
    category, existing_categories_names = validate_category_name(message)

    if category in existing_categories_names:
        logger.info('category already in DB, no need to inset!')
    else:
        logger.info('Inserting new category into category_manager table...')
        category_id = sp_client.supported_categories[category]
        db_provider.insert_record_to_table(table_name=category_manager_model.table_name,
                                           record=category_manager_model.create_category(category_id, category))

    return {'created': True}


@app.route('/entity/remove', methods=['POST'])
def entity_remove():
    message = request.get_json()
    category, existing_categories_names = validate_category_name(message)

    if category in existing_categories_names:
        db_provider.delete_record_from_table(table_name=category_manager_model.table_name,
                                             where_value="%s='%s'"
                                                         % (category_manager_model.key_category_name, category))

        db_provider.delete_record_from_table(table_name=spotify_tracker_model.table_name,
                                             where_value="%s='%s'"
                                                         % (spotify_tracker_model.key_category_name, category))

    return {'removed': True}


def do_category_tracking(curr_category, is_dry_run):
    logger.info('start tracking after category %s...', curr_category[category_manager_model.key_category_name])
    to_insert = []
    num_of_records = 0

    category_id = curr_category[category_manager_model.key_category_id]
    playlists_dict = sp_client.get_category_playlists(category_id)
    playlist_index = 1
    for playlist_id, playlist_name in playlists_dict.items():
        tracks = sp_client.get_playlist_tracks(playlist_id)
        for curr_track in tracks:
            artists_name_str = None
            if curr_track['artists'] is not None:
                artists_names = list(map(lambda x: x['name'], curr_track['artists']))
                if artists_names is not None:
                    artists_name_str = ','.join(artists_names)

            category_name = curr_category[category_manager_model.key_category_name]

            new_track = spotify_tracker_model.create_tracker(track_id=curr_track['id'],
                                                             category_name=category_name,
                                                             playlist_name=playlist_name,
                                                             playlist_ind=playlist_index,
                                                             track_ind=curr_track.get('track_number'),
                                                             track_name=curr_track.get('name'),
                                                             artist_name=artists_name_str,
                                                             popularity=curr_track.get('popularity'))
            to_insert.append(new_track)
            playlist_index += 1

    if not is_dry_run:
        try:
            num_of_records = db_provider.insert_batch_to_table(table_name=spotify_tracker_model.table_name,
                                                               rows_dict_list=to_insert)
        except Exception as e:
            logger.error('failed to insert tracks to db due to %s', e)

    db_provider.update_record_in_table(table_name=category_manager_model.table_name,
                                       set_value="%s='%s'" % (category_manager_model.key_track_date, int(time.time())),
                                       where_value="%s='%s'" % (category_manager_model.key_category_id, category_id))
    return num_of_records


def validate_category_name(message):
    category = message.get('categoryName')
    if category is None:
        abort(400, description='Bad request! field categoryName does not exists!')

    supported_categories_names = sp_client.supported_categories.keys()

    if category not in supported_categories_names:
        abort(400, description='Bad request! category name not supported by current spotify client.\n'
                               'Please choose from the supported categories:%s' % supported_categories_names)

    existing_categories_records = db_provider.get_records_from_table(table_name=category_manager_model.table_name,
                                                                     fields=category_manager_model.key_category_name)
    existing_categories_names = list(map(lambda x: x[category_manager_model.key_category_name],
                                         existing_categories_records))

    return category, existing_categories_names


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=constants.app_port)
