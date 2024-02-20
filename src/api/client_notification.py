from src.db.database_functions import get_connections_by_remaining_updates, get_connections_id_by_radio, \
    get_connections_id_by_current_radio
from src.api.search_request import search
from src.api.stream_request import radio_stream_event


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
