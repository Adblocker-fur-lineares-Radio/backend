import time
import requests
from threading import Thread

from api.db.database_functions import get_connections_by_remaining_updates, \
    get_radios_that_need_switch_by_time_and_update, get_connections_id_by_radio, \
    get_all_radios, get_radios_and_update_by_currently_playing, get_connections_id_by_current_radio
from api.db.db_helpers import NewTransaction
from api.search_request import search
from api.stream_request import radio_stream_event


def notify_client_search_update(connections):
    """
    Sends search(_update) to client
    @param connections: the connections that need to be updated
    @return: -
    """
    cons = get_connections_by_remaining_updates()
    for connection in cons:
        connections[connection.id].send(search(connection.id))


def notify_client_stream_guidance(connections, radio_id):
    """
    Sends either a stream_event if radio needs switch or update_event if not
    @param connections: the connections
    @param radio_id: the radio that gets updated or switched off from
    @return: -
    """
    cons = get_connections_id_by_radio(radio_id)
    for connection in cons:
        connections[connection].send(radio_stream_event(connection))


def notify_client_stream_metadata_guidance(connections, radio_id):
    """
    Sends either a stream_event if radio needs switch or update_event if not
    @param connections: the connections
    @param radio_id: the radio that gets updated or switched off from
    @return: -
    """
    cons = get_connections_id_by_current_radio(radio_id)
    for connection in cons:
        connections[connection].send(radio_stream_event(connection))


# SUBJECT TO CHANGE WITH TIMETABLE IMPLEMENTATION
def analyse_radio_stream(connections):
    """
    Endless loop that checks if radio needs switching, and calls search_update and stream_guidance
    Is replaced by fingerprint
    @param connections: the connections
    @return: -
    """

    while True:
        with NewTransaction():
            now = int(time.strftime('%M', time.localtime()))
            [streams, switch_time] = get_radios_that_need_switch_by_time_and_update(now)
            if len(streams) > 0:
                notify_client_search_update(connections)
            for stream in streams:
                notify_client_stream_guidance(connections, stream.id)

        if switch_time > now:
            sleep_time = switch_time - now
        else:
            sleep_time = 60 - now + switch_time
        time.sleep(sleep_time * 60 - int(time.strftime('%S', time.localtime())) + 1)


def update_metadata(radios):
    """
    Updates the current song of the radios with the metadata from radio.net
    :param radios: List of all radios
    :return: the radios, where a new song is playing
    """
    url = "https://prod.radio-api.net/stations/now-playing?stationIds="

    if not radios:
        url += "None"
    else:
        url += ','.join(radio.station_id for radio in radios)

    response = requests.get(url)
    data = response.json()
    need_update = get_radios_and_update_by_currently_playing(data)
    return need_update


def metadata_processing(connections):
    """
    Endless loop which updates the currently playing songs and sends them to the connections
    :param connections: the current connections
    :return: -
    """
    while True:
        with NewTransaction():
            radios = get_all_radios()
            streams = update_metadata(radios)
            if len(streams) > 0:
                notify_client_search_update(connections)
            for stream in streams:
                notify_client_stream_metadata_guidance(connections, stream.id)
        time.sleep(15)


def start_notifier(connections):
    """
    Starts thread for analyse_radio_stream to check for switching or update
    @param connections:
    @return: the thread
    """

    analysis = Thread(target=analyse_radio_stream, args=(connections,))
    metadata = Thread(target=metadata_processing, args=(connections,))
    analysis.start()
    metadata.start()
    return metadata
