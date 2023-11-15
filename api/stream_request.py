import json

from api.db.database_functions import switch_to_working_radio, get_radio_by_id, \
    update_preferences_for_connection, serialize


def radio_stream_event(connection_id):
    """
    Servers response to "stream_request", selecting one radio to be switched to
    @param connection_id: the specified connection
    @return: the radio to be switched to with a buffer
    """
    radio_id = switch_to_working_radio(connection_id)
    radio = get_radio_by_id(radio_id)

    return json.dumps({
        'type': 'radio_stream_event',
        'switch_to': serialize(radio),
        'buffer': 0
    })


def radio_update_event(radio_id):
    """
    Servers radio update
    @param radio_id: the specified radio
    @return: the serialized radio object
    """
    radio = get_radio_by_id(radio_id)

    return json.dumps({
        'type': 'radio_switch_event',
        'radio': serialize(radio),
    })


def stream_request(client, connection_id, req):
    """
    Client sends list of preferences, gets radio_stream_event response
    @param client: specified client
    @param connection_id: specified connection
    @param req: the requested preference changes
    @return: -
    """
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
