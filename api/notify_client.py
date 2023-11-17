import time
from threading import Thread

from api.db.database_functions import get_connections_by_radio_and_remaining_updates, \
    get_radios_that_need_switch_by_time_and_update, commit
from api.search_request import search
from api.stream_request import radio_stream_event, radio_update_event


def notify_client_search_update(connections, radio_id):
    """
    Sends search(_update) to client
    @param connections: the connections that need to be updated
    @param radio_id: the radio that triggered the search(_update)
    @return: -
    """
    cons = get_connections_by_radio_and_remaining_updates(radio_id)
    for con in cons:
        connections[con.id].send(search(con.id))


def notify_client_stream_guidance(connections, radio_id):
    """
    Sends either a stream_event if radio needs switch or update_event if not
    @param connections: the connections
    @param radio_id: the radio that gets updated or switched off from
    @return: -
    """
    cons = get_connections_by_radio_and_remaining_updates(radio_id)
    for connection, needs_switch in cons:
        if needs_switch:
            connections[connection.id].send(radio_stream_event(connection.id))
        else:
            connections[connection.id].send(radio_update_event(connection.current_radio_id))


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
                notify_client_search_update(connections, stream.id)
                notify_client_stream_guidance(connections, stream.id)
            commit()


def start_notifier(connections):
    """
    Starts thread for analyse_radio_stream to check for switching or update
    @param connections:
    @return: the thread
    """
    analysation = Thread(target=analyse_radio_stream, args=(connections))
    analysation.start()
    return analysation


# class Dummy2:
#     def __init__(self, id):
#         self.id = id
#
#     def send(self, msg):
#         print(f"sending {msg} to client {self.id}")
#
#
# class Dummy1:
#     def __getitem__(self, item):
#         return Dummy2(item)
#
#
# connection = Dummy1()
#
# start_notifier(connection)