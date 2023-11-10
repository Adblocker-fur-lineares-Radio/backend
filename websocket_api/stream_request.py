import json

from datenbank_pythonORM.Python.database_functions import switch_to_working_radio, get_radio_by_id, \
    update_preferences_for_connection, serialize


def stream_guidance(connection_id):
    radio_id = switch_to_working_radio(connection_id)
    radio = get_radio_by_id(radio_id)

    return json.dumps({
        'type': 'stream_guidance',
        'radio': serialize(radio),
        'buffer': 0
    })


def stream_request(client, connection_id, req):
    update_preferences_for_connection(
        connection_id,
        preferred_radios=req["preferred_radios"],
        preferred_genres=req["preferred_genres"],
        preference_ad=req["preferred_experience"]["ad"],
        preference_talk=req["preferred_experience"]["talk"],
        preference_music=req["preferred_experience"]["music"],
        preference_news=req["preferred_experience"]["news"]
    )

    client.send(stream_guidance(connection_id))
