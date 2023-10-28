import time
from threading import Thread
import random
from search_request import search
from websocket_api.stream_request import stream_guidance


def test_random_search_update(connections):
    while True:
        time.sleep(1)
        if len(connections) == 0:
            continue
        ids = [random.choice(list(connections.keys())) for _ in range(1)]
        for con in ids:
            connections[con].send(search(con))
        # TODO: update remaining_updates in db


def test_random_stream_request(connections):
    while True:
        time.sleep(1.3)
        if len(connections) == 0:
            continue
        ids = [random.choice(list(connections.keys())) for _ in range(1)]
        for con in ids:
            connections[con].send(stream_guidance(con))
        # TODO: update remaining_updates in db


def start_test(connections):
    Thread(target=test_random_search_update, args=(connections,)).start()
    Thread(target=test_random_stream_request, args=(connections,)).start()
