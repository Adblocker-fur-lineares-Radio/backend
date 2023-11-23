import time
from threading import Thread

from api.db.database_functions import get_connections_by_remaining_updates, \
    get_radios_that_need_switch_by_time_and_update, commit, get_connections_id_by_radio
from api.search_request import search
from api.stream_request import radio_stream_event, radio_update_event


def notify_client_search_update(connections):
    """
    Sends search(_update) to client
    @param connections: the connections that need to be updated
    @return: -
    """
    cons = get_connections_by_remaining_updates()
    for connection in cons:
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
    while True:
        now = int(time.strftime('%M', time.localtime()))
        [streams, switch_time] = get_radios_that_need_switch_by_time_and_update()

        print(switch_time, now)
        for stream in streams:
            notify_client_stream_guidance(connections, stream.id)
            notify_client_search_update(connections)
            commit()

        if switch_time >= now:
            sleep_time = switch_time - now
        else:
            sleep_time = 60 - now + switch_time
        time.sleep(sleep_time * 60 - int(time.strftime('%S', time.localtime())) + 1)


def start_notifier(connections):
    """
    Starts thread for analyse_radio_stream to check for switching or update
    @param connections:
    @return: the thread
    """
    analysation = Thread(target=analyse_radio_stream, args=(connections,))
    analysation.start()
    return analysation
