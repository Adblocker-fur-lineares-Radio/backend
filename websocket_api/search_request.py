import json


def search(connection_id):
    # TODO: connect to db
    requested_updates = 1  # TODO: from db
    return json.dumps({
        'type': 'search_update',
        'radios': [],
        'remaining_updates': requested_updates - 1
    })


def search_request(client, req):
    # TODO: connect to database, update search params in db
    client_id = 0  # TODO: from db
    client.send(search(client_id))


def search_update_request(client, req):
    if req['requested_updates'] <= 0:
        print("Warning: search_update_request: requested <= 0 updates (need to be > 0)")
        return

    # TODO: connect to database
    connection_id = 1  # TODO: comes from db
    remaining_updates = 0  # TODO: comes from db

    instant_update = remaining_updates <= 0

    remaining_updates = req['requested_updates']  # TODO: send to database

    if instant_update:
        client.send(search(connection_id))
