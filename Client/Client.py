import time
import vlc
import json
import asyncio
import websockets
from api.db.database_functions import delete_connection_from_db

address = "ws://185.233.107.253:5000/api"


def search_request(query, filter_ids=None, filter_without_ads=False, requested_updates=1):
    """
    Look up ServerAPI Documentation (Google Drive)
    @param query: Contains Search-text
    @param filter_ids: Contains preferred Radios
    @param filter_without_ads: bool, if you want ads or not
    @param requested_updates: Number of follow-up updates expected
    @return: json-string
    """
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
    """
    Look up ServerAPI Documentation (Google Drive)
    @param requested_updates: Number of follow-up updates expected
    @return: json-string
    """
    return (json.dumps({
        'type': 'search_update_request',
        'requested_updates': requested_updates
    }))


def stream_request(preferred_radios=None, preferred_genres=None, preferred_experience=None):
    """
    Look up ServerAPI Documentation (Google Drive)
    @param preferred_radios: One preferred radio or multiple radios
    @param preferred_genres: One preferred genre or multiple genre
    @param preferred_experience: bool, preferred experience ads-news-music
    @return: json-string
    """
    return (json.dumps({
        'type': 'stream_request',
        'preferred_radios': preferred_radios or [1],
        'preferred_genres': preferred_genres or [],
        'preferred_experience': preferred_experience or {'ad': False, 'news': True, 'music': True, 'talk': True}
    }))


def openJson(msg):
    """
    Converts Json-String in array
    @param msg: Json-String
    @return: Array
    """
    return json.loads(msg)


async def StartClient():
    """
    Starts Client -> connect to server -> asks for radio -> play radio -> permanently polling for update
    @return: returns only on Error
    """
    async with websockets.connect(address) as ws:

        await ws.send(stream_request())
        print(f'Client sent: {stream_request()}')

        msg = await ws.recv()
        print(f"Client received: {msg}")

        data = openJson(msg)
        if data["type"] != "radio_stream_event":
            print("Error No Valid answer received")
            return
        tmp = data["switch_to"]
        current_stream = tmp["stream_url"]
        buffer = data["buffer"]

        instance = vlc.Instance()
        player = instance.media_player_new()
        media = instance.media_new(current_stream)
        player.set_media(media)
        player.play()

        time.sleep(0.5)  # buffer
        player.set_pause(1)  # buffer
        time.sleep(buffer)  # buffer
        player.play()  # buffer

        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=100)
                if msg != "0":
                    print()
                    print(f"Client received: {msg}")
                    data2 = openJson(msg)

                    if data2["type"] == "search_update":
                        radios = data2["radios"]
                        remaining_updates = data2["remaining_updates"]
                        # do nothing

                    elif data2["type"] == "radio_switch_event":
                        player.stop()
                        media = instance.media_new(data2["switch_to"])
                        player.set_media(media)
                        player.play()

                        time.sleep(0.5)  # buffer
                        player.set_pause(1)  # buffer
                        time.sleep(buffer)  # buffer
                        player.play()  # buffer

                    elif data2["type"] == "stream_guidance":
                        print("Error Client already connected")
                        return

                    elif data2["type"] == "radio_update_event":
                        radio = data2["radio"]
                        # do nothing

                    else:
                        print("Error no matching funktion")
                        return

            except websockets.exceptions.ConnectionClosedOK:
                pass


if __name__ == '__main__':
    delete_connection_from_db(7)
    asyncio.run(StartClient())
