import time
import vlc
import json
import asyncio
import websockets
# from api.db.database_functions import delete_connection_from_db

# address = "ws://185.233.107.253:5000/api"
address = "ws://127.0.0.1:5000/api"


def search_request(requested_updates=1):
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
        'requested_updates': requested_updates
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


def stream_request(preferred_radios=None, preferred_experience=None):
    """
    Look up ServerAPI Documentation (Google Drive)
    @param preferred_radios: One preferred radio or multiple radios
    @param preferred_experience: bool, preferred experience ads-news-music
    @return: json-string
    """
    return (json.dumps({
        'type': 'stream_request',
        'preferred_radios': preferred_radios,
        'preferred_experience': preferred_experience or {'ad': False, 'news': True, 'music': True, 'talk': True}
    }))


async def StartClient():
    """
    Starts Client -> connect to server -> asks for radio -> play radio -> permanently polling for update
    @return: returns only on Error
    """
    async with websockets.connect(address) as ws:

        ##############################
        ##############################
        commit = stream_request(preferred_radios=[1, 2])
        ##############################
        ##############################

        await ws.send(commit)
        print(f'Client sent: {commit}')
        msg = await asyncio.wait_for(ws.recv(), timeout=300)
        print(f"Client received: {msg}")

        data = json.loads(msg)
        if data["type"] != "radio_stream_event":
            print(f"Error: No valid answer received: '{data['type']}' instead of 'radio_stream_event'")
            return

        instance = vlc.Instance()
        player = instance.media_player_new()
        media = instance.media_new(data["switch_to"]["stream_url"])
        player.set_media(media)
        player.play()

        time.sleep(0.5)  # buffer
        player.set_pause(1)  # buffer
        time.sleep(data["buffer"])  # buffer
        player.play()  # buffer

        commit = search_request(5)
        await ws.send(commit)
        print(f'Client sent: {commit}')

        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=300)
                print()
                print(f"Client received: {msg}")
                data2 = json.loads(msg)

                if data2["type"] == "search_update":
                    pass

                elif data2["type"] == "radio_stream_event":

                    player.stop()
                    media = instance.media_new(data2["switch_to"]["stream_url"])
                    player.set_media(media)
                    player.play()

                    time.sleep(0.5)  # buffer
                    player.set_pause(1)  # buffer
                    time.sleep(data2["buffer"])  # buffer
                    player.play()  # buffer

                elif data2["type"] == "radio_update_event":
                    pass

                else:
                    print("Error: No matching function")
                    return

            except websockets.exceptions.ConnectionClosedOK:
                pass


if __name__ == '__main__':
    asyncio.run(StartClient())
