import time

from src.db.database_functions import get_radios_that_need_switch_by_time_and_update
from src.db.db_helpers import NewTransaction
from src.api.client_notification import notify_client_search_update, notify_client_stream_guidance


# SUBJECT TO CHANGE WITH TIMETABLE IMPLEMENTATION
def analyse_radio_stream(connections):
    """
    Endless loop that checks if radio needs switching, and calls search_update and stream_guidance
    Is replaced by fingerprint
    @param connections: the connections
    @return: -
    """

    while True:
        with NewTransaction():
            now = int(time.strftime('%M', time.localtime()))
            [streams, switch_time] = get_radios_that_need_switch_by_time_and_update(now)
            if len(streams) > 0:
                notify_client_search_update(connections)
            for stream in streams:
                notify_client_stream_guidance(connections, stream.id)

        if switch_time > now:
            sleep_time = switch_time - now
        else:
            sleep_time = 60 - now + switch_time
        time.sleep(sleep_time * 60 - int(time.strftime('%S', time.localtime())) + 1)
