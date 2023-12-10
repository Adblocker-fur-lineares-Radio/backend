import json

from api.db.database_functions import switch_to_working_radio, get_radio_by_id, \
    update_preferences_for_connection
from api.db.db_helpers import NewTransaction, serialize
import logging

from api.error_handling.error_checkers import check_valid_stream_request
from api.error_handling.error_classes import InternalError, Error
from logs.logging_config import configure_logging
configure_logging()

logger = logging.getLogger("stream_request.py")


def stream_request(client, connection_id, req):
    """
    Client sends list of preferences, gets radio_stream_event response
    @param client: specified client
    @param connection_id: specified connection
    @param req: the requested preference changes
    @return: -
    """

    with NewTransaction():
        check_valid_stream_request(req)
        update_preferences_for_connection(
            connection_id,
            preferred_radios=req["preferred_radios"],
            preference_ad=req["preferred_experience"]["ad"],
            preference_talk=req["preferred_experience"]["talk"],
            preference_music=req["preferred_experience"]["music"],
            preference_news=req["preferred_experience"]["news"]
        )
        response = radio_stream_event(connection_id)
    client.send(response)


def radio_stream_event(connection_id):
    """
    Servers response to "stream_request", selecting one radio to be switched to
    @param connection_id: the specified connection
    @return: the radio to be switched to with a buffer
    """
    if connection_id is None:
        raise InternalError(logger, "radio_stream_event(): parameter connection_id can't be None")

    radio_id = switch_to_working_radio(connection_id)

    if radio_id is None:
        raise Error("Couldn't find any radio to switch to. We are sorry.")

    radio = get_radio_by_id(radio_id)
    if radio is None:
        raise InternalError(logger, "radio_stream_event(): Couldn't find radio by id (id previously given by switch_to_working_radio())")

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

    if radio_id is None:
        raise InternalError(logger, "radio_update_event(): Parameter radio_id mustn't be None")

    radio = get_radio_by_id(radio_id)
    if radio is None:
        raise InternalError(logger, "radio_update_event(): given radio_id doesn't lead to an entry in db")

    return json.dumps({
        'type': 'radio_switch_event',
        'radio': serialize(radio),
    })




