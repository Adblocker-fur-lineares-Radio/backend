import logging
from dejavu.recognize import FileRecognizer
from dejavu import Dejavu
import time
from urllib.request import urlopen, Request
import os
import threading
from datetime import datetime
from api.db.database_functions import get_all_radios
from api.db.db_helpers import NewTransaction
import queue

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


def record(radio_stream_url, radio_name, offset, duration, q):
    while True:
        try:
            fname2 = "2_" + radio_name + str(time.perf_counter())[2:] + ".wav"
            f2 = open(fname2, 'wb')
            fname3 = "3_" + radio_name + str(time.perf_counter())[2:] + ".wav"
            f3 = open(fname3, 'wb')

            req = Request(radio_stream_url, headers={'User-Agent': "Magic Browser"})
            response = urlopen(req, timeout=10.0)
            i = 3
            while True:
                start = time.time()
                while time.time() - start <= duration - offset:
                    audio = response.read(1024)
                    if audio:
                        f2.write(audio)
                        if start + duration - 2 * offset < time.time():
                            f3.write(audio)

                f2.close()
                ftmp = fname2
                q.put(ftmp)
                fname2 = str(i) + "_" + str(radio_name) + "_" + str(time.perf_counter())[2:] + ".wav"
                f2 = open(fname2, 'wb')
                i += 1

                while time.time() - start <= 2 * duration - offset:
                    audio = response.read(1024)
                    if audio:
                        f3.write(audio)
                        if start + 2 * duration - 2 * offset < time.time():
                            f2.write(audio)
                f3.close()
                ftmp2 = fname3
                q.put(ftmp2)
                fname3 = str(i) + "_" + str(radio_name) + "_" + str(time.perf_counter())[2:] + ".wav"
                f3 = open(fname3, 'wb')
                i += 1

        except Exception as e:
            logger.error("Fingerprint Thread crashed: " + str(radio_name) + ": " + str(e))
            time.sleep(10)


def fingerprint(q, FingerThreshold):
    djv = Dejavu(config)
    while True:
        if q.qsize() > 0:
            datei = q.get()
            try:
                if os.stat(datei).st_size > 0:
                    finger = djv.recognize(FileRecognizer, datei)
                    if finger and finger["confidence"] > FingerThreshold:
                        logger.info(datei.split("_")[1] + ": " + str(finger))
                        q.task_done()
                        os.remove(datei)
                    else:
                        q.task_done()
                        os.remove(datei)
                else:
                    logger.error("File is empty: " + datei)
                    q.task_done()
                    os.remove(datei)
            except Exception as e:
                q.task_done()
                os.remove(datei)
                logger.error("Error: " + str(e))


def start_fingerprint(connections):
    djv = Dejavu(config)
    djv.fingerprint_directory("AD_SameLenghtJingles", [".wav"])

    test = os.listdir(os.getcwd())
    for item in test:
        if item.endswith(".wav"):
            os.remove(os.path.join(os.getcwd(), item))

    q = queue.Queue()
    a = threading.Thread(target=fingerprint, args=(q, 10))
    b = threading.Thread(target=fingerprint, args=(q, 10))
    c = threading.Thread(target=fingerprint, args=(q, 10))
    d = threading.Thread(target=fingerprint, args=(q, 10))

    with NewTransaction():
        radios = get_all_radios()
        threads = [threading.Thread(target=record, args=(radio.stream_url, radio.name, 0.6, 5, q)) for radio in
                   radios]

    threads.insert(0, a)
    threads.insert(0, b)
    threads.insert(0, c)
    threads.insert(0, d)

    for fingerprint_thread in threads:
        fingerprint_thread.start()

    return threads
