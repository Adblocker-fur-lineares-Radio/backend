import json

from backend.api.db.database_functions import switch_to_working_radio, get_radio_by_id, \
    update_preferences_for_connection, serialize
from error import check_valid_stream_request, error


def radio_stream_event(connection_id):
    if connection_id is None:
        print("radio_stream_event: Missing connection_id")
        return error("internal error")
    else:
        radio_id = switch_to_working_radio(connection_id)
        if radio_id is None:
            print("radio_stream_event: Missing radio_id")
            return error("internal error")
        else:
            radio = get_radio_by_id(radio_id)
            if radio is None:
                print("radio_stream_event: Missing radio")
                return error("internal error")
            else:
                return json.dumps({
                    'type': 'radio_stream_event',
                    'switch_to': serialize(radio),
                    'buffer': 0
                })


def radio_update_event(radio_id):
    if radio_id is None:
        print("radio_update_event: Missing radio_id")
        return error("internal error")
    else:
        radio = get_radio_by_id(radio_id)
        if radio is None:
            print("radio_update_event: Missing radio")
            return error("internal error")
        else:
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
