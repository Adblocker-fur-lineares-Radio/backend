import vlc
import json
import time
import asyncio

import websockets
from websockets.sync.client import connect


def CheckPollingUpdate(ws):
    check = ws.recv()
    if check:
        return check
    else:
        return 0


async def NeededResponse(ws):
    response_json = await ws.recv()
    return response_json


async def Connect2Server():
    async with websockets.connect("ws://localhost:1234") as ws:
        return ws


def search_request(ws, query, filter_ids=None, filter_without_ads=False, requested_updates=1):
    ws.send(json.dumps({
        'type': 'search_request',
        'query': query,
        'requested_updates': requested_updates,
        'filter': {
            'ids': filter_ids,
            'without_ads': filter_without_ads
        }
    }))


def search_update_request(ws, requested_updates=1):
    ws.send(json.dumps({
        'type': 'search_update_request',
        'requested_updates': requested_updates
    }))


def stream_request(ws, preferred_radios=None, preferred_genres=None, preferred_experience=None):
    ws.send(json.dumps({
        'type': 'stream_request',
        'preferred_radios': preferred_radios or [],
        'preferred_genres': preferred_genres or [],
        'preferred_experience': preferred_experience or {'ad': False, 'news': True, 'music': True}
    }))


def StartClient():
    ws = asyncio.run((Connect2Server()))
    stream_request(ws)
    response = NeededResponse(ws)
    data = json.load(open(response))

    if data["type"] == "stream_guidance":
        url = data["radio"]
        buffer = data["buffer"]
    else:
        print("Error 404")
        return

    current_stream = url

    # url1 = 'https://wdr-wdr2-rheinruhr.icecastssl.wdr.de/wdr/wdr2/rheinruhr/mp3/56/stream.mp3?aggregator=surfmusik-de&1697723004'
    # url2 = 'https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3?aggregator=radio-de'

    instance = vlc.Instance('--input-repeat=-1', '--fullscreen')
    player = instance.media_player_new()
    media = instance.media_new(current_stream)
    player.set_media(media)
    player.play()

    while 1:
        check = CheckNeededUpdate(ws)
        if check == 0:
            print("loop")
        else:
            print("Change")
            # do something


if __name__ == '__main__':
    StartClient()
