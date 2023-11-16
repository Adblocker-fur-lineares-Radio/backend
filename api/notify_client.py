import time
from threading import Thread

from api.db.database_functions import get_connections_by_radio_and_remaining_updates, get_connections_by_radio, \
    get_radios_that_need_switch_by_time_and_update, commit
from api.search_request import search
from api.stream_request import radio_stream_event, radio_update_event


def notify_client_search_update(connections, radio_id):
    cons = get_connections_by_radio_and_remaining_updates(radio_id)
    for con in cons:
        connections[con.id].send(search(con.id))


def notify_client_stream_guidance(connections, radio_id):
    cons = get_connections_by_radio(radio_id)
    for connection, needs_switch in cons:
        if needs_switch:
            connections[connection.id].send(radio_stream_event(connection.id))
        else:
            connections[connection.id].send(radio_update_event(connection.current_radio_id))


def analyse_radio_stream(connections):
    switch_time = None
    while True:
        if switch_time is None or switch_time == int(time.strftime('%M', time.localtime())):
            [streams, switch_time] = get_radios_that_need_switch_by_time_and_update()
            print(switch_time)
            for stream in streams:
                notify_client_search_update(connections, stream.id)
                notify_client_stream_guidance(connections, stream.id)
            commit()

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


def start_notifier(connections):

    analysation = Thread(target=analyse_radio_stream, args=(connections))
    analysation.start()
    return analysation

