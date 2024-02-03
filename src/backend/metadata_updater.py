import logging
import time
import requests
from threading import Thread

from src.db.database_functions import get_all_radios, get_radios_and_update_by_currently_playing
from src.db.db_helpers import NewTransaction
from src.logging_config import configure_logging
from src.api.client_notification import notify_client_stream_metadata_guidance, notify_client_search_update

configure_logging()
logger = logging.getLogger("metadata_updater.py")


def split_song_and_interpret(title):
    currently_playing = title.split(': ')

    if len(currently_playing) == 1:
        currently_playing = title.split(' - ')

    if len(currently_playing) == 1:
        currently_playing.insert(0, '')

    return {
        'song': currently_playing[1],
        'interpret': currently_playing[0],
    }


def update_metadata(radios):
    """
    Updates the current song of the radios with the metadata from radio.net
    :param radios: List of all radios
    :return: the radios, where a new song is playing
    """

    api1_radios = [radio.station_id for radio in radios if radio.metadata_api == 1]
    api2_radios = [radio.station_id for radio in radios if radio.metadata_api == 2]
    metadatas = []

    # radio.de API
    if len(api1_radios):
        url = "https://prod.radio-api.net/stations/now-playing?stationIds="
        url += ','.join(radio for radio in api1_radios)
        response = requests.get(url).json()
        metadatas.extend({
            'station_id': radio['stationId'],
            **split_song_and_interpret(radio['title'])
        } for radio in response)

    # nrwlokalradios API
    for radio in api2_radios:
        url = f"https://api-prod.nrwlokalradios.com/playlist/current?station={radio}"
        response = requests.get(url).json()
        metadatas.append({
             'station_id': response['station_id'],
             'song': response['title'],
             'interpret': response['artist']
         })

    need_update = get_radios_and_update_by_currently_playing(metadatas)
    return need_update


def metadata_processing(connections):
    """
    Endless loop which updates the currently playing songs and sends them to the connections
    :param connections: the current connections
    :return: -
    """
    while True:
        try:
            with NewTransaction():
                radios = get_all_radios()
                streams = update_metadata(radios)
                if len(streams) > 0:
                    notify_client_search_update(connections)
                for stream in streams:
                    notify_client_stream_metadata_guidance(connections, stream.id)
            time.sleep(15)
        except Exception as e:
            logger.error(f"Error in updating metadata: {e}")


def start_notifier(connections):
    """
    Starts thread for analyse_radio_stream to check for switching or update
    @param connections:
    @return: the thread
    """

    metadata = Thread(target=metadata_processing, args=(connections,))
    metadata.start()
    return metadata
