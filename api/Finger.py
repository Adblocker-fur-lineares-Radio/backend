import logging
import os
import threading
import queue
from time import time, sleep
from tempfile import NamedTemporaryFile
from urllib.request import urlopen, Request
from dejavu.recognize import FileRecognizer
from dejavu import Dejavu
from logging_config import csv_logging_write
from dotenv import load_dotenv

from api.db.database_functions import get_all_radios
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

STREAM_AUTO_RESTART = 6 * 60 * 60 - 10 * 60  # 6h - 10min

class FilenameInfo:
    def __init__(self, filename):
        filename = str(filename)
        self.filename = filename
        splitted = filename.split('_')
        self.radio_name = splitted[0]
        self.status = splitted[1]
        self.type = splitted[2]


skip_timers = {}
SKIP_TIME = 5  # 5 seconds
skip_mutex = threading.Lock()


def start_skip_time(radio_name):
    with skip_mutex:
        skip_timers[radio_name] = time()


def needs_skipping(radio_name):
    with skip_mutex:
        if radio_name in skip_timers:
            return time() - skip_timers[radio_name] <= SKIP_TIME
    return False


def read_for(response, seconds):
    chunk = b""
    start = time()
    while time() - start < seconds:
        audio = response.read(1024)
        if audio:
            chunk += audio
    return chunk


def record(radio_stream_url, radio_name, offset, duration, queue):
    while True:
        try:
            ThreadStart = time()

            req = Request(radio_stream_url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urlopen(req, timeout=10.0)

            piece = NamedTemporaryFile(delete=False)

            # init file with 'offset' seconds
            audio = read_for(response, offset)
            piece.write(audio)

            while True:
                # restart after giving time (so we won't get kicked out)
                if time() - ThreadStart >= STREAM_AUTO_RESTART:
                    response.close()
                    break

                # fill file with rest except overlapping audio
                # (has already 'offset' seconds and next overlapping would be 'offset' => 2 * offset)
                audio = read_for(response, duration - 2 * offset)
                piece.write(audio)

                # now read overlapping that will be put into both files
                overlapping = read_for(response, offset)
                piece.write(overlapping)

                # file is ready
                piece.flush()
                piece.close()
                if not needs_skipping(radio_name):
                    queue.put((radio_name, piece.name))

                # create next file
                piece = NamedTemporaryFile(delete=False)
                piece.write(overlapping)

        except Exception as e:
            logger.error("Fingerprint Thread crashed: " + str(radio_name) + ": " + str(e))
            sleep(10)


def fingerprint(q, FingerThreshold):
    djv = Dejavu(config)
    while True:
        radio_name, filename = q.get()
        try:
            if os.stat(filename).st_size > 0:
                finger = djv.recognize(FileRecognizer, filename)
                if finger and finger["confidence"] > FingerThreshold:
                    info = FilenameInfo(finger["song_name"])
                    logger.info(radio_name + ": " + str(finger) + f"\n{radio_name}: {info.radio_name} - {info.status} - {info.type}, confidence = {finger['confidence']}")
                    csv_logging_write([radio_name, "Werbung"], "adtime.csv")
                    start_skip_time(radio_name)
            else:
                logger.error("File is empty: " + radio_name)
        except Exception as e:
            logger.error("Fingerprinting Error in " + radio_name + ": " + str(e))
        finally:
            q.task_done()
            os.remove(filename)


def start_fingerprint(connections):
    djv = Dejavu(config)
    djv.fingerprint_directory("AD_SameLenghtJingles", [".wav"])

    test = os.listdir(os.getcwd())
    for item in test:
        if item.endswith(".wav"):
            os.remove(os.path.join(os.getcwd(), item))

    q = queue.Queue()
    a = threading.Thread(target=fingerprint, args=(q, 20))
    b = threading.Thread(target=fingerprint, args=(q, 20))
    c = threading.Thread(target=fingerprint, args=(q, 20))
    d = threading.Thread(target=fingerprint, args=(q, 20))

    with NewTransaction():
        radios = get_all_radios()
        threads = [threading.Thread(target=record, args=(radio.stream_url, radio.name, 1, 5, q)) for radio in
                   radios]

    threads.append(a)
    threads.append(b)
    threads.append(c)
    threads.append(d)

    for fingerprint_thread in threads:
        fingerprint_thread.start()

    return threads
