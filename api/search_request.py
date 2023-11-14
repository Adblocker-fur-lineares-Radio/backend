import json

from backend.api.db.database_functions import get_connection, get_radio_by_query, \
    update_search_request_for_connection, get_connection_favorites, update_search_remaining_updates, serialize
from error import *


def search(connection_id):
    connection = get_connection(connection_id)
    favorites = get_connection_favorites(connection_id)
    radios = get_radio_by_query(
        search_query=connection.search_query,
        search_without_ads=connection.search_without_ads,
        ids=[fav.radio_id for fav in favorites])

    remaining_updates = update_search_remaining_updates(connection_id)

    return json.dumps({
        'type': 'search_update',
        'radios': serialize(radios),
        'remaining_updates': remaining_updates
    })


def search_request(client, connection_id, req):
    if check_valid_search_request(client, req):
        update_search_request_for_connection(
            connection_id,
            requested_updates=req["requested_updates"],
            search_query=req["query"],
            without_ads=req["filter"]["without_ads"],
            ids=req["filter"]["ids"]
        )
        client.send(search(connection_id))


def search_update_request(client, connection_id, req):
    if check_valid_search_update_request(client, req):

        # FIXME: possible "race condition": reading 'remaining_updates', possibly triggering instant update,
        #  then setting it

        connection = get_connection(connection_id)
        instant_update = connection.search_remaining_update <= 0
        remaining_updates = req['requested_updates']
        update_search_remaining_updates(connection_id, remaining_updates)
        if instant_update:
            client.send(search(connection_id))
