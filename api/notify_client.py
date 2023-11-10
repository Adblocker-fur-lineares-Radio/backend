from threading import Thread

from api.db.database_functions import get_connections_by_radio_and_remaining_updates, get_connections_by_radio, \
    get_radios_that_need_switch_by_time
from api.search_request import search
from api.stream_request import radio_stream_event, radio_update_event


def notify_client_search_update(radio_id):
    cons = get_connections_by_radio_and_remaining_updates(radio_id)
    for con in cons:
        connections[con.id].send(search(con.id))


def notify_client_stream_guidance(radio_id):
    cons = get_connections_by_radio(radio_id)
    for connection, needs_switch in cons:
        if needs_switch:
            connections[connection.id].send(radio_stream_event(connection.id))
        else:
            connections[connection.id].send(radio_update_event(connection.current_radio_id))


def analyse_radio_stream():
    streams = get_radios_that_need_switch_by_time()
    for stream in streams:
        notify_client_search_update(stream.id)
        # todo: db updaten


# TODO DB-Funktion für die Radios anstatt Klasse zu benutzen
#radios = get_radio_by_id(connections)

connections = {}

radio1 = notify_clients_test_classes.Radio
radio2 = notify_clients_test_classes.Radio
radios = [radio1, radio2]

guidance = Thread(target=notify_client_stream_guidance())
analysation = Thread(target=analyse_radio_stream())

guidance.start()
analysation.start()

guidance.join()
analysation.join()
