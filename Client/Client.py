import time
import vlc
import json
import asyncio
import websockets
from dejavu.recognize import FileRecognizer

# from api.db.database_functions import delete_connection_from_db

address = "ws://185.233.107.253:5000/api"
from dejavu import Dejavu
import time
import sys
from urllib.request import urlopen


# address = "ws://127.0.0.1:5000/api"


def search_request(requested_updates=1):
    """
    Look up ServerAPI Documentation (Google Drive)
    @param query: Contains Search-textS
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



def test():
    config = {
        "database": {
            "host": "localhost",
            "user": "test123",
            "password": "test123",
            "database": "finger"
        },
    }
    djv = Dejavu(config)
    djv.fingerprint_directory(r"..\OrginalAudio", [".wav"])
    print(djv.db.get_num_fingerprints())

    # print(djv.recognize(FileRecognizer, r"C:\Users\kaany\Desktop\WerbungTest.mp3"))
    # print(djv.recognize(FileRecognizer, r"C:\Users\kaany\Desktop\NoneTest.mp3"))
    # print(djv.recognize(FileRecognizer, r"C:\Users\kaany\Desktop\Orginal\1live_news.mp3"))
    # print(djv.recognize(FileRecognizer, r"C:\Users\kaany\Desktop\Orginal\1live_werbung.mp3"))
    # print(djv.recognize(FileRecognizer, r"C:\Users\kaany\Desktop\Orginal\bayern1_news.mp3"))
    # print(djv.recognize(FileRecognizer, r"C:\Users\kaany\Desktop\Orginal\bayern1_werbung.mp3"))
    # print(djv.recognize(FileRecognizer, r"C:\Users\kaany\Desktop\Orginal\wdr2_news.mp3"))
    # print(djv.recognize(FileRecognizer, r"C:\Users\kaany\Desktop\Orginal\wdr2_werbung.mp3"))
    # return

    response = urlopen("https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3?aggregator=radio-de",
                       timeout=10.0)

    fname1 = "1_" + str(time.perf_counter())[2:] + ".wav"
    f1 = open(fname1, 'wb')

    fname2 = "2_" + str(time.perf_counter())[2:] + ".wav"
    f2 = open(fname2, 'wb')

    fname3 = "3_" + str(time.perf_counter())[2:] + ".wav"
    f3 = open(fname3, 'wb')

    start = time.time()
    offset = 2
    dauer = 10

    while True:  # wird einmalig ausgeführt
        try:
            audio = response.read(1024)

            if start + dauer - offset < time.time() < start + 2 * dauer - offset:  # 2. Block first offset Part
                f2.write(audio)
                sys.stdout.flush()

            if time.time() <= start + dauer:  # 1. Block
                f1.write(audio)
                sys.stdout.flush()
            else:
                break

        except Exception as e:
            print("Error " + str(e))

    f1.close()
    sys.stdout.flush()
    print(djv.recognize(FileRecognizer, fname1))
    i = 4

    while True:  # wird dauerhaft ausgeführt
        start = time.time()
        try:
            while time.time() - start < dauer - offset:
                audio = response.read(1024)
                if start < time.time() < start + dauer - offset:
                    f2.write(audio)
                    sys.stdout.flush()
                if start + dauer - 2 * offset < time.time() < start + dauer - offset:
                    f3.write(audio)
                    sys.stdout.flush()

            f2.close()
            sys.stdout.flush()
            print(djv.recognize(FileRecognizer, fname2))
            fname2 = str(i) + "_" + str(time.perf_counter())[2:] + ".wav"
            f2 = open(fname2, 'wb')
            i += 1

            while time.time() - start < 2 * dauer - offset:
                audio = response.read(1024)
                if start + dauer < time.time() < start + 2 * dauer - offset:
                    f3.write(audio)
                    sys.stdout.flush()
                if start + 2 * dauer - 2 * offset < time.time() < start + 2 * dauer - offset:
                    f2.write(audio)
                    sys.stdout.flush()

            f3.close()
            sys.stdout.flush()
            print(djv.recognize(FileRecognizer, fname3))
            fname3 = str(i) + "_" + str(time.perf_counter())[2:] + ".wav"
            f3 = open(fname3, 'wb')
            i += 1

        except Exception as e:
            print("Error " + str(e))


if __name__ == '__main__':
    # asyncio.run(StartClient())
    test()

    # pip install git+https://github.com/yunpengn/dejavu.git
    # pip install mysql
    # ffmpeg: https://phoenixnap.com/kb/ffmpeg-windows
