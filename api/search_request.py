import json

from api.db.database_functions import get_connection, get_radio_by_query, \
    update_search_request_for_connection, get_connection_favorites, update_search_remaining_updates, serialize
from error import check_valid_search_update_request, check_valid_search_request, error


def search(connection_id):
    """
    Searches DB for connection and its preferences
    @param connection_id: the specified connection
    @return: the connection information in json format
    """
    if connection_id is None:
        print("search: Missing connection_id")
        return error("internal error")
    else:
        connection = get_connection(connection_id)
        if connection is None:
            print("search: Missing connection")
            return error("internal error")
        else:
            favorites = get_connection_favorites(connection_id)
            if favorites is None:
                print("search: Missing favorites")
                return error("internal error")
            else:
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
    """
    Client requests to change connection preferences, gets search(_update) response
    @param client: specified client
    @param connection_id: specified connection
    @param req: connection information to be changed
    @return: -
    """
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
    """
    Client requests to receive updates, gets search(_update) response if instant_update is enabled
    @param client: specified client
    @param connection_id: specified connection
    @param req: requested updates
    @return: -
    """
    if check_valid_search_update_request(client, req):

        # FIXME: possible "race condition": reading 'remaining_updates', possibly triggering instant update,
        #  then setting it
        connection = get_connection(connection_id)
        if connection is None:
            print("search_update_request: Missing connection")
            client.send(error("internal error"))
        else:
            instant_update = connection.search_remaining_update <= 0
            remaining_updates = req['requested_updates']
            update_search_remaining_updates(connection_id, remaining_updates)
            if instant_update:
                client.send(search(connection_id))
