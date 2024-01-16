import datetime
import logging
import os
import threading
import queue
from time import time, sleep
from tempfile import NamedTemporaryFile
from urllib.request import urlopen, Request
from dejavu.recognize import FileRecognizer
from dejavu import Dejavu

from api.configs import FINGERPRINT_MYSQL_HOST, FINGERPRINT_MYSQL_USER, FINGERPRINT_MYSQL_PASSWORD, \
    FINGERPRINT_MYSQL_DB, FINGERPRINT_SKIP_TIME_AFTER_AD_START, STREAM_AUTO_RESTART, AD_FALLBACK_TIMEOUT, \
    CONFIDENCE_THRESHOLD, FINGERPRINT_WORKER_THREAD_COUNT, PIECE_OVERLAP, PIECE_DURATION, STREAM_TIMEOUT, \
    FINGERPRINT_PIECE_MIN_SIZE, FINGERPRINT_SKIP_TIME_AFTER_ARTIFICIAL_AD_END
from logging_config import csv_logging_write
from api.db.database_functions import (get_all_radios, get_radio_by_name, set_radio_status_to_music,
                                       reset_radio_ad_until, set_radio_ad_until, set_radio_status_to_ad)
from api.notify_client import notify_client_stream_guidance, notify_client_search_update
from api.db.db_helpers import NewTransaction, STATUS

logger = logging.getLogger("Finger.py")

config = {
    "database": {
        "host": FINGERPRINT_MYSQL_HOST,
        "user": FINGERPRINT_MYSQL_USER,
        "password": FINGERPRINT_MYSQL_PASSWORD,
        "database": FINGERPRINT_MYSQL_DB
    },
}

skip_timers = {}
skip_mutex = threading.Lock()


class FilenameInfo:
    def __init__(self, filename):
        try:
            self.filename = filename.decode("utf-8")
            parts = self.filename.split('_')
            self.radio_name = parts[0]
            self.status = parts[1]
            self.type = parts[2]
        except Exception as e:
            raise f"Fingerprinted filename {filename} has an incorrect format"


def start_skip_time(radio_name, duration):
    with skip_mutex:
        skip_timers[radio_name] = time() + duration


def needs_skipping(radio_name):
    with skip_mutex:
        if radio_name in skip_timers:
            return skip_timers[radio_name] > time()
    return False


def read_for(response, seconds):
    chunk = b""
    start = time()
    while time() - start < seconds:
        audio = response.read(1024)
        if audio:
            chunk += audio
    return chunk


def record(radio_stream_url, radio_name, offset, duration, job_queue):
    while True:
        try:
            ThreadStart = time()

            req = Request(radio_stream_url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urlopen(req, timeout=STREAM_TIMEOUT)

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

                # now read overlapping that will be put into both files
                overlapping = read_for(response, offset)

                # check if stream still works and write the temporary file
                pieceData = audio + overlapping
                if len(pieceData) < FINGERPRINT_PIECE_MIN_SIZE:
                    response.close()
                    raise Exception(f"Couldn't receive any data (len = {len(pieceData)} < {FINGERPRINT_PIECE_MIN_SIZE})")
                piece.write(pieceData)

                # file is ready
                piece.flush()
                piece.close()
                if not needs_skipping(radio_name):
                    job_queue.put((radio_name, piece.name))

                # create next file
                piece = NamedTemporaryFile(delete=False)
                piece.write(overlapping)

        except Exception as e:
            logger.error(f"Record stream of {radio_name} crashed: {e}")
            sleep(10)


def fingerprint(job_queue, confidence_threshold, connections):
    djv = Dejavu(config)
    while True:
        with NewTransaction():
            radio_name, filename = job_queue.get()
            radio = get_radio_by_name(radio_name)
            try:
                if radio.ad_until and radio.ad_until <= datetime.datetime.now().minute:
                    set_radio_status_to_music(radio.id)
                    reset_radio_ad_until(radio.id)
                    notify_client_stream_guidance(connections, radio.id)
                    notify_client_search_update(connections)
                    start_skip_time(radio_name, FINGERPRINT_SKIP_TIME_AFTER_ARTIFICIAL_AD_END)
                    logger.info(radio_name + ' artifical end of ad')
                    csv_logging_write([radio_name, "end_of_ad_artificial"], "adtime.csv")

                elif radio.ad_until is None or radio.ad_duration == 0:
                    finger = djv.recognize(FileRecognizer, filename)
                    if finger and finger["confidence"] > confidence_threshold:
                        info = FilenameInfo(finger["song_name"])
                        start_skip_time(radio_name, FINGERPRINT_SKIP_TIME_AFTER_AD_START)

                        if radio.status_id == STATUS['ad']:
                            reset_radio_ad_until(radio.id)
                            set_radio_status_to_music(radio.id)
                            csv_logging_write([radio_name, "end_of_ad"], "adtime.csv")

                        elif radio.status_id == STATUS['music']:
                            set_radio_status_to_ad(radio.id)
                            if radio.ad_duration > 0:
                                set_radio_ad_until(radio.id, datetime.datetime.now().minute + radio.ad_duration)
                            else:
                                set_radio_ad_until(radio.id, datetime.datetime.now().minute + AD_FALLBACK_TIMEOUT)
                            csv_logging_write([radio_name, "start_of_ad"], "adtime.csv")

                        notify_client_stream_guidance(connections, radio.id)
                        notify_client_search_update(connections)

                        logger.info(radio_name + ": " + str(finger) +
                                    f"\n{radio_name}: " +
                                    f"{info.radio_name} - {info.status} - {info.type}" +
                                    f", confidence = {finger['confidence']}")
            except Exception as e:
                logger.error(f"Fingerprinting Error in {radio_name}: {e}")
            finally:
                job_queue.task_done()
                os.remove(filename)


def start_fingerprint(connections):
    djv = Dejavu(config)
    djv.fingerprint_directory("AD_SameLenghtJingles", [".wav"])

    job_queue = queue.Queue()

    # add the worker threads
    threads = [threading.Thread(target=fingerprint, args=(job_queue, CONFIDENCE_THRESHOLD, connections)) for _ in range(FINGERPRINT_WORKER_THREAD_COUNT)]

    with NewTransaction():
        radios = get_all_radios()
        threads.extend([threading.Thread(target=record, args=(radio.stream_url, radio.name, PIECE_OVERLAP, PIECE_DURATION, job_queue))
                        for radio in radios])

    for fingerprint_thread in threads:
        fingerprint_thread.start()

    return threads
