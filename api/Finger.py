import logging
from api.logging_config import csv_logging_write
from dejavu.recognize import FileRecognizer
from dejavu import Dejavu
import time
from urllib.request import urlopen
import os
import threading
from datetime import datetime, timedelta
from api.notify_client import notify_client_search_update, notify_client_stream_guidance
from api.db.database_functions import get_all_radios, set_radio_status_to_ad, set_radio_status_to_music, get_radio_by_id
from api.db.db_helpers import NewTransaction

from dotenv import load_dotenv

load_dotenv()
FINGERPRINT_MYSQL_HOST = os.getenv('FINGERPRINT_MYSQL_HOST')
FINGERPRINT_MYSQL_USER = os.getenv('FINGERPRINT_MYSQL_USER')
FINGERPRINT_MYSQL_PASSWORD = os.getenv('FINGERPRINT_MYSQL_PASSWORD')
FINGERPRINT_MYSQL_DB = os.getenv('FINGERPRINT_MYSQL_DB')

logger = logging.getLogger("Finger.py")

config = {
    "database": {
        "host": FINGERPRINT_MYSQL_HOST,
        "user": FINGERPRINT_MYSQL_USER,
        "password": FINGERPRINT_MYSQL_PASSWORD,
        "database": FINGERPRINT_MYSQL_DB
    },
}


def fingerprinting(radio_id, offset, duration, finger_threshold, connections):
    status_change_time = None
    with NewTransaction():
        radio = get_radio_by_id(radio_id)
    while True:
        try:
            if status_change_time and status_change_time == datetime.now() and radio['status_id'] == 1:
                with NewTransaction():
                    radio['status_id'] = 2
                    set_radio_status_to_music(radio['id'])
                    notify_client_search_update(connections)
                    notify_client_stream_guidance(connections, radio['id'])
                status_change_time = None
            logger.info(radio['name'])
            djv = Dejavu(config)
            fname2 = "2_" + radio['name'] + str(time.perf_counter())[2:] + ".wav"
            f2 = open(fname2, 'wb')
            fname3 = "3_" + radio['name'] + str(time.perf_counter())[2:] + ".wav"
            f3 = open(fname3, 'wb')

            response = urlopen(radio['stream_url'], timeout=10.0)
            i = 3
            while True:


                start = time.time()
                while time.time() - start <= duration - offset:
                    audio = response.read(1024)
                    f2.write(audio)
                    if start + duration - 2 * offset < time.time():
                        f3.write(audio)
                f2.close()

                try:
                    if os.stat(fname2).st_size > 0:
                        finger2 = djv.recognize(FileRecognizer, fname2)
                        if finger2 and finger2["confidence"] > finger_threshold:
                            logger.info(datetime.now().strftime("%H:%M:%S") + ": " + str(finger2))
                            info = finger2["song_name"].decode().split("_")
                            if str(info[1]) == 'Werbung':
                                csv_logging_write([str(info[0]), info[2]], 'adtime.csv')
                                if radio['status_id'] == 2:
                                    with NewTransaction():
                                        radio['status_id'] = 1
                                        set_radio_status_to_ad(radio['id'])
                                        notify_client_search_update(connections)
                                        notify_client_stream_guidance(connections, radio['id'])
                                        time.sleep(radio['ad_duration'] * 60)
                                        if radio['ad_duration'] > 0:
                                            radio['status_id'] = 2
                                            set_radio_status_to_music(radio['id'])
                                            notify_client_search_update(connections)
                                            notify_client_stream_guidance(connections, radio['id'])
                                        else:
                                            status_change_time = datetime.now() + timedelta(minutes=6)
                                if radio['status_id'] == 1:
                                    with NewTransaction():
                                        radio['status_id'] = 2
                                        set_radio_status_to_music(radio['id'])
                                        notify_client_search_update(connections)
                                        notify_client_stream_guidance(connections, radio['id'])
                except Exception as e:
                    logger.error("Error " + str(radio['name']) + ": " + str(e))

                os.remove(fname2)
                fname2 = str(i) + "_" + str(time.perf_counter())[2:] + ".wav"
                f2 = open(fname2, 'wb')
                i += 1

                while time.time() - start <= 2 * duration - offset:
                    audio = response.read(1024)
                    f3.write(audio)
                    if start + 2 * duration - 2 * offset < time.time():
                        f2.write(audio)
                f3.close()

                try:
                    if os.stat(fname3).st_size > 0:
                        finger3 = djv.recognize(FileRecognizer, fname3)
                        if finger3 and finger3["confidence"] > finger_threshold:
                            logger.info(datetime.now().strftime("%H:%M:%S") + ": " + str(finger3))
                            info = finger3["song_name"].decode().split("_")
                            if str(info[1]) == 'Werbung':
                                csv_logging_write([str(info[0]), info[2]], 'adtime.csv')

                                if radio['status_id'] == 2:
                                    with NewTransaction():
                                        radio['status_id'] = 1
                                        set_radio_status_to_ad(radio['id'])
                                        notify_client_search_update(connections)
                                        notify_client_stream_guidance(connections, radio['id'])
                                        time.sleep(radio['ad_duration'] * 60)
                                        if radio['ad_duration'] > 0:
                                            set_radio_status_to_music(radio['id'])
                                            notify_client_search_update(connections)
                                            set_radio_status_to_music(radio['id'])
                                            radio['status_id'] = 2
                                        else:
                                            status_change_time = datetime.now() + timedelta(minutes=6)

                                if radio['status_id'] == 1:
                                    with NewTransaction():
                                        radio['status_id'] = 2
                                        set_radio_status_to_music(radio['id'])
                                        notify_client_search_update(connections)
                                        notify_client_stream_guidance(connections, radio['id'])
                except Exception as e:
                    logger.error("Error " + str(radio['name']) + ": " + str(e))

                os.remove(fname3)
                fname3 = str(i) + "_" + str(time.perf_counter())[2:] + ".wav"
                f3 = open(fname3, 'wb')
                i += 1

        except Exception as e:
            logger.error("Fingerprint Thread crashed: " + str(radio['name']) + ": " + str(e))
            time.sleep(10)


def start_fingerprint(connections):
    djv = Dejavu(config)
    djv.fingerprint_directory("AD_SameLenghtJingles", [".wav"])
    with NewTransaction():
        radios = get_all_radios()
        threads = [threading.Thread(target=fingerprinting, args=(radio.id, 1, 8, 15, connections))for radio in radios]

    for fingerprint_thread in threads:
        fingerprint_thread.start()

    return threads
