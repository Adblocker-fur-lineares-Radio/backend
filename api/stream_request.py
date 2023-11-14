import json

from backend.api.db.database_functions import switch_to_working_radio, get_radio_by_id, \
    update_preferences_for_connection, serialize
from error import *


def radio_stream_event(connection_id):
    radio_id = switch_to_working_radio(connection_id)
    radio = get_radio_by_id(radio_id)

    return json.dumps({
        'type': 'radio_stream_event',
        'switch_to': serialize(radio),
        'buffer': 0
    })


def radio_update_event(radio_id):
    radio = get_radio_by_id(radio_id)

    return json.dumps({
        'type': 'radio_switch_event',
        'radio': serialize(radio),
    })


def stream_request(client, connection_id, req):
    if check_valid_stream_request(client, req):
        update_preferences_for_connection(
            connection_id,
            preferred_radios=req["preferred_radios"],
            preferred_genres=req["preferred_genres"],
            preference_ad=req["preferred_experience"]["ad"],
            preference_talk=req["preferred_experience"]["talk"],
            preference_music=req["preferred_experience"]["music"],
            preference_news=req["preferred_experience"]["news"]
        )
        client.send(radio_stream_event(connection_id))


