from datetime import datetime
from threading import Thread
import notify_clients_test_classes
import json


def search(connection_id, radio_list):
    requested_updates = 1
    return json.dumps({
        'type': 'search_update',
        'radios': radio_list,
        'remaining_updates': requested_updates - 1
    })

def stream_guidance(connection_id, radio_name):
    return json.dumps({
        'type': 'stream_guidance',
        'radios': {'name': 'Test Radio'},
        'buffer': 0
    })

def notify_client_search_update(radio):
    for con in connections:
        if con.remaining_updates >= 1:
            # preferred_radios = get_preferred_radios(con_id)
            for pref in con.preferred_radio:
                if pref == radio:
                    #TODO remaining_updates = -1
                    if radio.status_id == 1: #Werbung:
                        if con.without_ads:
                            con.send(search(con.id, con.prefered_radio.remove(radio)))
                        else:
                            con.send(search(con.id, con.prefered_radio))
                    else:
                        con.send(search(con.id, con.prefered_radio))
                    break


def notify_client_stream_guidance():
    #TODO currently playing bei connection hinzufügen
    for con in connections:
        for radio in con.prefered_radios:
            if radio.status_id != 1:  #Werbung
                if con.currently_playing is None or con.currently_playing != radio:
                    con.currently_playing = radio
                    con.send(stream_guidance(con.id, radio))
                    break


def analyse_radio_stream():
    for stream in radios:
        if stream.ad_transmission_start < datetime.now().hour < stream.ad_transmission_end:
            #TODO status in DB updaten
            if stream.ad_start_time <= datetime.now().minute <= stream.ad_end_time:
                if stream.status != 'Werbung':
                    stream.status = 'Werbung'
                    notify_client_search_update(stream)

            elif stream.status != 'Musik':
                stream.status = 'Musik'
                notify_client_search_update(stream)


# TODO DB-Funktion für die Radios anstatt Klasse zu benutzen
#radios = get_radio_by_id(connections)

connections = {}

radio1 = notify_clients_test_classes.Radio
radio2 = notify_clients_test_classes.Radio
radios = [radio1, radio2]

guidance = Thread(target=notify_client_stream_guidance())
analysation = Thread(target=analyse_radio_stream())

guidance.start()
analysation.start()

guidance.join()
analysation.join()
