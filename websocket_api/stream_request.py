import json


def stream_guidance(connection_id):
    return json.dumps({
        'type': 'stream_guidance',
        'radios': {'name': 'Test Radio'},
        'buffer': 0
    })


def stream_request(client, req):
    # TODO: update preferred_radios, preferred_genres, preferred_experience
    connection_id = 1
    client.send(stream_guidance(connection_id))
