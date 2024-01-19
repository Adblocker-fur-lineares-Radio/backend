from datetime import datetime, timedelta
import logging
import multiprocessing
import os
import threading
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

            logger.info(f"Started recording chunks of {radio_name}")

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
                    raise Exception(f"Couldn't receive enough data (len = {len(pieceData)} < {FINGERPRINT_PIECE_MIN_SIZE})")
                piece.write(pieceData)

                # file is ready
                piece.flush()
                piece.close()
                if not needs_skipping(radio_name):
                    # FIXME when fingerprinting gets heavily delayed `radio` could be outdated
                    with NewTransaction():
                        radio = get_radio_by_name(radio_name)
                        job_queue.put((radio, piece.name))

                # create next file
                piece = NamedTemporaryFile(delete=False)
                piece.write(overlapping)

        except Exception as e:
            logger.error(f"Record stream of {radio_name} crashed: {e}")
            sleep(10)


def action_handler(action_queue, connections):
    while True:
        action, radio = action_queue.get()
        try:
            with NewTransaction():
                if action == "end_of_ad_artificial":
                    set_radio_status_to_music(radio.id)
                    reset_radio_ad_until(radio.id)
                    notify_client_stream_guidance(connections, radio.id)
                    notify_client_search_update(connections)
                    start_skip_time(radio.name, FINGERPRINT_SKIP_TIME_AFTER_ARTIFICIAL_AD_END)
                    logger.info(radio.name + ' artifical end of ad')
                    csv_logging_write([radio.name, "end_of_ad_artificial"], "adtime.csv")
                elif action == "end_of_ad":
                    reset_radio_ad_until(radio.id)
                    set_radio_status_to_music(radio.id)
                    csv_logging_write([radio.name, "end_of_ad"], "adtime.csv")
                elif action == "start_of_ad":
                    start_skip_time(radio.name, FINGERPRINT_SKIP_TIME_AFTER_AD_START)
                    set_radio_status_to_ad(radio.id)
                    if radio.ad_duration > 0:
                        set_radio_ad_until(radio.id, datetime.now() + timedelta(minutes=radio.ad_duration))
                    else:
                        set_radio_ad_until(radio.id, datetime.now() + timedelta(seconds=AD_FALLBACK_TIMEOUT))
                    csv_logging_write([radio.name, "start_of_ad"], "adtime.csv")

                notify_client_stream_guidance(connections, radio.id)
                notify_client_search_update(connections)
        except Exception as e:
            logger.error(f"Fingerprinting Error in {radio.name}: {e}")
        finally:
            action_queue.task_done()


def fingerprint(job_queue, action_queue, confidence_threshold):
    djv = Dejavu(config)
    while True:
        radio, filename = job_queue.get()
        # logger.info(f"analysing chunk for radio {radio.name}")
        try:
            if radio.ad_until and radio.ad_until <= datetime.datetime.now().minute:
                action_queue.put(("end_of_ad_artificial", radio))

            elif radio.ad_until is None or radio.ad_duration == 0:
                finger = djv.recognize(FileRecognizer, filename)
                if finger and finger["confidence"] > confidence_threshold:
                    info = FilenameInfo(finger["song_name"])

                    if radio.status_id == STATUS['ad']:
                        action_queue.put(("end_of_ad", radio))
                    elif radio.status_id == STATUS['music']:
                        action_queue.put(("start_of_ad", radio))

                    logger.info(radio.name + ": " + str(finger) +
                                f"\n{radio.name}: " +
                                f"{info.radio_name} - {info.status} - {info.type}" +
                                f", confidence = {finger['confidence']}")

        except Exception as e:
            logger.error(f"Fingerprinting Error in {radio.name}: {e}")
        finally:
            job_queue.task_done()
            os.remove(filename)


# def check_artificial_end_regularly(interval_seconds, radios, action_queue):
#     while True:
#         for radio in radios:
#             action_queue.put(("check_artificial_end", radio.name))
#         sleep(interval_seconds)


def start_fingerprint(connections):
    djv = Dejavu(config)
    djv.fingerprint_directory("AD_SameLenghtJingles", [".wav"])

    # job_queue = queue.Queue()
    job_queue = multiprocessing.Manager().Queue()
    action_queue = multiprocessing.Manager().Queue()

    # add the worker threads
    workers = [multiprocessing.Process(target=fingerprint, args=(job_queue, action_queue, CONFIDENCE_THRESHOLD)) for _ in range(FINGERPRINT_WORKER_THREAD_COUNT)]

    with NewTransaction():
        radios = get_all_radios()
        recorders = [threading.Thread(target=record, args=(radio.stream_url, radio.name, PIECE_OVERLAP, PIECE_DURATION, job_queue))
                     for radio in radios]

    for recorder in recorders:
        recorder.start()

    for worker in workers:
        worker.start()

    action_thread = threading.Thread(target=action_handler, args=(action_queue, connections))
    action_thread.start()

    # # check every minute
    # action_end_check_thread = threading.Thread(target=check_artificial_end_regularly, args=(radios, 60, action_queue))
    # action_end_check_thread.start()

    # return [*recorders, *workers, action_thread, action_end_check_thread]
    return [*recorders, *workers, action_thread]
