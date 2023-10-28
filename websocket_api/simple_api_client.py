from websocket import create_connection
import json
import time
import threading


def request_search(ws, query, filter_ids=None, filter_without_ads=False, requested_updates=1):
    ws.send(json.dumps({
        'type': 'search_request',
        'query': query,
        'requested_updates': requested_updates,
        'filter': {
            'ids': filter_ids,
            'without_ads': filter_without_ads
        }
    }))


def request_stream(ws, preferred_radios=None, preferred_genres=None, preferred_experience=None):
    ws.send(json.dumps({
        'type': 'stream_request',
        'preferred_radios': preferred_radios or [],
        'preferred_genres': preferred_genres or [],
        'preferred_experience': preferred_experience or {'ad': False, 'talk': True, 'news': True, 'music': True}
    }))


ws = create_connection("ws://localhost:5000/api")


def make_requests(ws):
    request_search(ws, "test", requested_updates=5)
    print("sent search_request")
    time.sleep(0.5)
    request_stream(ws, preferred_radios=[1], preferred_genres=[1])
    print("sent stream_request")


def receive(ws):
    try:
        while True:
            print(f"{json.loads(ws.recv())}")
    except KeyboardInterrupt:
        ws.close()


t1 = threading.Thread(target=receive, args=(ws,))
t2 = threading.Thread(target=make_requests, args=(ws,))

t1.start()
t2.start()

t1.join()
t2.join()


