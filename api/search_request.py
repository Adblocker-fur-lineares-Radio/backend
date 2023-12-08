import json

from api.db.database_functions import get_connection, get_radio_by_query, update_search_remaining_updates, serialize, \
    commit
from error import get_or_raise, InternalError
import logging
from logs.logging_config import configure_logging
configure_logging()

logger = logging.getLogger("search_request.py")


def search(connection_id):
    """
    Searches DB for connection and its preferences
    @param connection_id: the specified connection
    @return: the connection information in json format
    """
    if connection_id is None:
        logger.error("search(): parameter connection_id can't be None")
        raise InternalError()

    connection = get_connection(connection_id)
    if connection is None:
        logger.error("search(): Couldn't find connection in database")
        raise InternalError()

    radios = get_radio_by_query()

    remaining_updates = update_search_remaining_updates(connection_id)
    commit()

    # TODO: add possibility for advanced filters

    return json.dumps({
        'type': 'search_update',
        'radios': serialize(radios),
        'remaining_updates': remaining_updates
    })


def search_request(client, connection_id, req):
    """
    Client requests to change connection preferences, gets search(_update) response
    @param client: specified client
    @param connection_id: specified connection
    @param req: connection information to be changed
    @return: -
    """

    # TODO add possibility to have filters

    requested_updates = get_or_raise(req, "requested_updates")
    update_search_remaining_updates(connection_id, requested_updates)
    commit()

    client.send(search(connection_id))


def search_update_request(client, connection_id, req):
    """
    Client requests to receive updates, gets search(_update) response if instant_update is enabled
    @param client: specified client
    @param connection_id: specified connection
    @param req: requested updates
    @return: -
    """

    connection = get_connection(connection_id)
    if connection is None:
        logger.error("search_update_request(): Couldn't find connection in database")
        raise InternalError()

    instant_update = connection.search_remaining_update <= 0
    remaining_updates = get_or_raise(req, 'requested_updates')

    update_search_remaining_updates(connection_id, remaining_updates)
    commit()

    if instant_update:
        client.send(search(connection_id))
