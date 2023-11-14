import json

from api.db.database_functions import get_connection, get_radio_by_query, \
    update_search_request_for_connection, get_connection_favorites, update_search_remaining_updates, serialize


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
    update_search_request_for_connection(
        connection_id,
        requested_updates=req["requested_updates"],
        search_query=req["query"],
        without_ads=req["filter"]["without_ads"],
        ids=req["filter"]["ids"])

    client.send(search(connection_id))


def search_update_request(client, connection_id, req):
    if req['requested_updates'] <= 0:
        print("Warning: search_update_request: requested <= 0 updates (need to be > 0)")
        return

    # FIXME: possible "race condition": reading 'remaining_updates', possibly triggering instant update, then setting it

    connection = get_connection(connection_id)

    instant_update = connection.search_remaining_update <= 0

    remaining_updates = req['requested_updates']

    update_search_remaining_updates(connection_id, remaining_updates)

    if instant_update:
        client.send(search(connection_id))
