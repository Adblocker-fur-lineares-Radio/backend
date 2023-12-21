import logging
from api.logging_config import csv_logging_write
from dejavu.recognize import FileRecognizer
from dejavu import Dejavu
import time
from urllib.request import urlopen
import os
import threading
from datetime import datetime
from api.notify_client import notify_client_search_update, notify_client_stream_guidance
from api.db.database_functions import get_all_radios, set_radio_to_ad_status,get_connections_id_by_radio, \
                                       get_connections_by_remaining_updates
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


def fingerprinting(radio, offset, duration, finger_threshold,connections):
    while True:
        try:
            djv = Dejavu(config)

            fname2 = "2_" + str(time.perf_counter())[2:] + ".wav"
            f2 = open(fname2, 'wb')
            fname3 = "3_" + str(time.perf_counter())[2:] + ".wav"
            f3 = open(fname3, 'wb')

            response = urlopen(radio.stream_url, timeout=10.0)
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
                            if str(info[1]) == 'Werbung' and radio.name in info[0]:
                                csv_logging_write([str(info[0]), info[2]], 'adtime.csv')
                                set_radio_to_ad_status(radio)
                                notify_client_search_update(connections)
                                notify_client_stream_guidance(connections, radio.id)
                                time.sleep(radio.ad_duration * 60)
                except Exception as e:
                    logger.error("Error " + str(e))

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
                            if str(info[1]) == 'Werbung' and radio.name in info[0]:
                                csv_logging_write([str(info[0]), info[2]], 'adtime.csv')
                                set_radio_to_ad_status(radio)
                                notify_client_search_update(connections)
                                notify_client_stream_guidance(connections, radio.id)
                                time.sleep(radio.ad_duration * 60)
                except Exception as e:
                    logger.error("Error " + str(e))

                os.remove(fname3)
                fname3 = str(i) + "_" + str(time.perf_counter())[2:] + ".wav"
                f3 = open(fname3, 'wb')
                i += 1

        except Exception as e:
            logger.error("Fingerprintthread crashed: " + str(e))
            time.sleep(10)


def start_fingerprint(connections):
    djv = Dejavu(config)
    djv.fingerprint_directory("Jingles", [".wav"])
    # radios = [
    #     ["https://f131.rndfnk.com/ard/wdr/1live/live/mp3/128/stream.mp3?aggregator=radio-de&cid=01FBRZTS1K1TCD4KA2YZ1ND8X3&sid=2ZgOD39nA4EtSY3oeiU1mg7NEqn&token=T3AJgSK9quR8fmsSqvUmAeKyjM0Xl_YULkvmCOCZ4Uc&tvf=KnSoVLnHoRdmMTMxLnJuZGZuay5jb20", "1Live"],
    #     ["https://d121.rndfnk.com/ard/wdr/wdr2/rheinland/mp3/128/stream.mp3?cid=01FBS03TJ7KW307WSY5W0W4NYB&sid=2WfgdbO7GvnQL9AwD8vhvPZ9fs0&token=cz5XFBkPm158lD9VGL4JxM-2zzMfE_3qEd-sX_kdaAA&tvf=x6sCXJp9jRdkMTIxLnJuZGZuay5jb20", "WDR 2"],
    #     ["https://d121.rndfnk.com/ard/br/br1/franken/mp3/128/stream.mp3?cid=01FCDXH5496KNWQ5HK18GG4HED&sid=2ZDBcNAOweP69799K4rCsFc3Jgw&token=AaURPm1j9atmzP6x_QnojyKUrDLXmpuME5vqVWX1ZI0&tvf=XJJyGEmbnhdkMTIxLnJuZGZuay5jb20", "BAYERN 1"],
    #     ["https://audiotainment-sw.streamabc.net/atsw-bigfm-aac-128-6355201?sABC=65802q7r%230%23rn9sqqp8s62pno3o9nn36nr41n95oo44%23enqvbqr&aw_0_1st.playerid=radiode&amsparams=playerid:radiode;skey:1702899070", "BigFM"],
    #     ["https://dashitradio-stream28.radiohost.de/dashitradio_128?ref=radiode", "100,5"],
    #     ["https://antenneac--di--nacs-ais-lgc--04--cdn.cast.addradio.de/antenneac/live/mp3/high?ar-distributor=f0a0&_art=dj0yJmlwPTkxLjU3LjI0OS4yMzQmaWQ9aWNzY3hsLTdmc2Vhc2ltYiZ0PTE3MDI5ODU2MjEmcz03ODY2ZjI5YyNhMDYxOTllYTEwM2FlYzM0MTYyNDE1YzY2YTRjNDA0OA", "AntenneAC"],
    #     ["https://d111.rndfnk.com/ard/rb/bremennext/live/mp3/128/stream.mp3?aggregator=radio-de&cid=01FC1W7JCTNQQ1J99JMF830D6A&sid=2ZiK4GavxtgsSaqtdowtdwysXnP&token=gsPLApWuDcXT2mizNStYL-aellTCTRzPgxKcfpRpQrs&tvf=yOB7cYH9oRdkMTExLnJuZGZuay5jb20", "BremenNext"],
    #     ["https://radiorst--di--nacs-ais-lgc--0c--cdn.cast.addradio.de/radiorst/live/aac/low?ar-distributor=f0a0&_art=dj0yJmlwPTkxLjU3LjI0OS4yMzQmaWQ9aWNzY3hsLTZpYml1Z2VwYiZ0PTE3MDI5ODU3MTUmcz03ODY2ZjI5YyNhZDUzNWQ2MGZhYjg3N2UxODZmMGFmZDVhYTE4YmViZA", "RST"],
    # ]

    radios = get_all_radios()

    threads = [threading.Thread(target=fingerprinting, args=(radio, 2, 8, 15, connections))
               for radio in radios]

    for thread in threads:
        thread.start()

    return threads


if __name__ == '__main__':
    threads = start_fingerprint()
    for thread in threads:
        thread.join()
