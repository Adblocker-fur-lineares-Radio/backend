import logging
from api.logging_config import csv_logging_write
from dejavu.recognize import FileRecognizer
from dejavu import Dejavu
import time
from urllib.request import urlopen, Request
import os
import threading
from datetime import datetime
from api.notify_client import notify_client_search_update, notify_client_stream_guidance
from api.db.database_functions import get_all_radios, set_radio_status_to_ad, set_radio_status_to_music
from api.db.db_helpers import NewTransaction
import numpy as np

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


def fingerprinting(radio_stream_url, radio_name, offset, duration, finger_threshold, connections, radio_id, radio_ad_duration, radio_status):
    while True:
        try:
            djv = Dejavu(config)
            fname2 = "1" + "_" + str(radio_name) + "_" + str(time.perf_counter())[2:] + ".wav"
            f2 = open(fname2, 'wb')
            fname3 = "2" + "_" + str(radio_name) + "_" + str(time.perf_counter())[2:] + ".wav"
            f3 = open(fname3, 'wb')

            req = Request(radio_stream_url, headers={'User-Agent': "Magic Browser"})
            response = urlopen(req, timeout=10.0)
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
                        #logger.info(finger2)
                        if finger2 and finger2["confidence"] > finger_threshold:
                            logger.info(datetime.now().strftime("%H:%M:%S") + ": " + str(finger2))
                            info = finger2["song_name"].decode().split("_")
                            if str(info[1]) == 'Werbung':
                                csv_logging_write([str(info[0]), info[2]], 'adtime.csv')
                                if radio_status == 2:
                                    with NewTransaction():
                                        radio_status = 1
                                        set_radio_status_to_ad(radio_id)
                                        notify_client_search_update(connections)
                                        notify_client_stream_guidance(connections, radio_id)
                                        time.sleep(radio_ad_duration * 60)
                                        if radio_ad_duration > 0:
                                            radio_status = 2
                                            set_radio_status_to_music(radio_id)
                                            notify_client_search_update(connections)
                                            notify_client_stream_guidance(connections, radio_id)

                                if radio_status == 1:
                                    with NewTransaction():
                                        radio_status = 2
                                        set_radio_status_to_music(radio_id)
                                        notify_client_search_update(connections)
                                        notify_client_stream_guidance(connections, radio_id)
                except Exception as e:
                    logger.error("Error " + str(radio_name) + ": Fingerprinting error: ")

                os.remove(fname2)
                fname2 = str(i) + "_" + str(radio_name) + "_" + str(time.perf_counter())[2:] + ".wav"
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
                        #logger.info(finger3)
                        if finger3 and finger3["confidence"] > finger_threshold:
                            logger.info(datetime.now().strftime("%H:%M:%S") + ": " + str(finger3))
                            info = finger3["song_name"].decode().split("_")
                            if str(info[1]) == 'Werbung':
                                csv_logging_write([str(info[0]), info[2]], 'adtime.csv')

                                if radio_status == 2:
                                    with NewTransaction():
                                        radio_status = 1
                                        set_radio_status_to_ad(radio_id)
                                        notify_client_search_update(connections)
                                        notify_client_stream_guidance(connections, radio_id)
                                        time.sleep(radio_ad_duration * 60)
                                        if radio_ad_duration > 0:
                                            set_radio_status_to_music(radio_id)
                                            notify_client_search_update(connections)
                                            set_radio_status_to_music(radio_id)
                                            radio_status = 2

                                if radio_status == 1:
                                    with NewTransaction():
                                        radio_status = 2
                                        set_radio_status_to_music(radio_id)
                                        notify_client_search_update(connections)
                                        notify_client_stream_guidance(connections, radio_id)
                except Exception as e:
                    logger.error("Error " + str(radio_name) + ": Fingerprinting error: ")

                os.remove(fname3)
                fname3 = str(i) + "_" + str(radio_name) + "_" + str(time.perf_counter())[2:] + ".wav"
                f3 = open(fname3, 'wb')
                i += 1

        except Exception as e:
            logger.error("Fingerprint Thread crashed: " + str(radio_name) + ": " + str(e))
            test = os.listdir(os.getcwd())
            for item in test:
                if item.endswith(".wav") and str(radio_name) in item:
                    os.remove(os.path.join(os.getcwd(), item))
            time.sleep(10)


def start_fingerprint(connections):
    np.seterr(divide='ignore')
    djv = Dejavu(config)
    djv.fingerprint_directory("AD_SameLenghtJingles", [".wav"])

    test = os.listdir(os.getcwd())
    for item in test:
        if item.endswith(".wav"):
            os.remove(os.path.join(os.getcwd(), item))

    with NewTransaction():
        radios = get_all_radios()
        threads = [threading.Thread(target=fingerprinting, args=(radio.stream_url, radio.name, 1, 8, 15, connections, radio.id, radio.ad_duration, radio.status_id)) for radio in radios]

    for fingerprint_thread in threads:
        fingerprint_thread.start()

    return threads
