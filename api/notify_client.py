import time
from threading import Thread

from api.db.database_functions import get_connections_by_radio_and_remaining_updates, \
    get_radios_that_need_switch_by_time_and_update, commit, get_connections_id_by_radio
from api.search_request import search
from api.stream_request import radio_stream_event, radio_update_event


def notify_client_search_update(connections, radio_id):
    """
    Sends search(_update) to client
    @param connections: the connections that need to be updated
    @param radio_id: the radio that triggered the search(_update)
    @return: -
    """
    for connection in connections:
        connections[connection].send(search(connection))


def notify_client_stream_guidance(connections, radio_id):
    """
    Sends either a stream_event if radio needs switch or update_event if not
    @param connections: the connections
    @param radio_id: the radio that gets updated or switched off from
    @return: -
    """
    cons = get_connections_id_by_radio(radio_id)
    print(cons)
    for connection in cons[0]:
        connections[connection].send(radio_stream_event(connection))


# SUBJECT TO CHANGE WITH TIMETABLE IMPLEMENTATION
def analyse_radio_stream(connections):
    """
    Endless loop that checks if radio needs switching, and calls search_update and stream_guidance
    @param connections: the connections
    @return: -
    """
    switch_time = None
    while True:
        if switch_time is None or switch_time == int(time.strftime('%M', time.localtime())):
            [streams, switch_time] = get_radios_that_need_switch_by_time_and_update()
            for stream in streams:
                print(stream)
                notify_client_stream_guidance(connections, stream.id)
                notify_client_search_update(connections, stream.id)
            commit()


def start_notifier(connections):
    """
    Starts thread for analyse_radio_stream to check for switching or update
    @param connections:
    @return: the thread
    """
    analysation = Thread(target=analyse_radio_stream, args=(connections,))
    analysation.start()
    return analysation
