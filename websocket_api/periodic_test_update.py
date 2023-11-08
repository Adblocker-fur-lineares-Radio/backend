import time
from threading import Thread
import random
from search_request import search
from websocket_api.stream_request import stream_guidance

from datenbank_pythonORM.Python.database_functions import commit, update_search_remaining_updates


def test_random_search_update(connections):
    while True:
        time.sleep(10)
        if len(connections) == 0:
            continue
        ids = [random.choice(list(connections.keys())) for _ in range(1)]
        for con in ids:
            connections[con].send(search(con))
            update_search_remaining_updates(con)  # decrements
        commit()


def test_random_stream_request(connections):
    time.sleep(5)
    while True:
        time.sleep(10)
        if len(connections) == 0:
            continue
        ids = [random.choice(list(connections.keys())) for _ in range(1)]
        for con in ids:
            connections[con].send(stream_guidance(con))
            update_search_remaining_updates(con)  # decrements
        commit()


def start_test(connections):
    Thread(target=test_random_search_update, args=(connections,)).start()
    Thread(target=test_random_stream_request, args=(connections,)).start()
