import vlc
import json
import asyncio
import websockets


async def CheckPollingUpdate():
    async with websockets.connect("ws://localhost:1234") as ws:
        check = await ws.recv()
        if check:
            return check
        else:
            return 0


async def NeededResponse():
    async with websockets.connect("ws://localhost:1234") as ws:
        response_json = await ws.recv()
        return response_json


def search_request(query, filter_ids=None, filter_without_ads=False, requested_updates=1):
    return (json.dumps({
        'type': 'search_request',
        'query': query,
        'requested_updates': requested_updates,
        'filter': {
            'ids': filter_ids,
            'without_ads': filter_without_ads
        }
    }))


def search_update_request(requested_updates=1):
    return (json.dumps({
        'type': 'search_update_request',
        'requested_updates': requested_updates
    }))


def stream_request(preferred_radios=None, preferred_genres=None, preferred_experience=None):
    return (json.dumps({
        'type': 'stream_request',
        'preferred_radios': preferred_radios or [],
        'preferred_genres': preferred_genres or [],
        'preferred_experience': preferred_experience or {'ad': False, 'news': True, 'music': True}
    }))


def openJson(input2):
    return json.loads(input2)


def playRadio(current_stream):
    instance = vlc.Instance('--input-repeat=-1', '--fullscreen')
    player = instance.media_player_new()
    media = instance.media_new(current_stream)
    player.set_media(media)
    player.play()
    while 1:
        pass


async def StartClient():
    async with websockets.connect("ws://localhost:1234") as ws:
        name = input("What's your name? ")
        await ws.send(name)
        print(f'Client sent: {name}')

        greeting = await ws.recv()
        print(f"Client received: {greeting}")

        await ws.send(stream_request())
        print(f'Client sent: {stream_request()}')

        stream_guidance = await ws.recv()
        print(f"Client received: {stream_guidance}")

        data = openJson(stream_guidance)
        current_stream = data["radio"]

        playRadio(current_stream)


if __name__ == '__main__':
    asyncio.run(StartClient())
