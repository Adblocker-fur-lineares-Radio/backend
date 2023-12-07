import vlc
import json
import asyncio
import websockets
from dejavu.recognize import FileRecognizer
from dejavu import Dejavu
import time
import sys
from urllib.request import urlopen

address = "ws://185.233.107.253:5000/api"
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

    response = urlopen("https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3?aggregator=radio-de",timeout=10.0)
    response2 = urlopen("https://d121.rndfnk.com/ard/wdr/wdr2/rheinland/mp3/128/stream.mp3?cid=01FBS03TJ7KW307WSY5W0W4NYB&sid=2WfgdbO7GvnQL9AwD8vhvPZ9fs0&token=cz5XFBkPm158lD9VGL4JxM-2zzMfE_3qEd-sX_kdaAA&tvf=x6sCXJp9jRdkMTIxLnJuZGZuay5jb20",timeout=10.0)
    response3 = urlopen("https://stream.dashitradio.de/dashitradio/mp3-128/stream.mp3?ref", timeout=10.0)
    response4 = urlopen("https://antenneac--di--nacs-ais-lgc--06--cdn.cast.addradio.de/antenneac/live/mp3/high",timeout=10.0)
    response5 = urlopen("https://stream.bigfm.de/saarland/aac-128", timeout=10.0)
    response6 = urlopen("https://d121.rndfnk.com/ard/br/br1/franken/mp3/128/stream.mp3?cid=01FCDXH5496KNWQ5HK18GG4HED&sid=2ZDBcNAOweP69799K4rCsFc3Jgw&token=AaURPm1j9atmzP6x_QnojyKUrDLXmpuME5vqVWX1ZI0&tvf=XJJyGEmbnhdkMTIxLnJuZGZuay5jb20", timeout=10.0)

    fname1_1lve = "1_" + "1Live" + ".wav"
    f1_1lve = open(fname1_1lve, 'wb')
    fname2_1lve = "2_" + "1Live" + ".wav"
    f2_1lve = open(fname2_1lve, 'wb')
    fname3_1lve = "3_" + "1Live" + ".wav"
    f3_1lve = open(fname3_1lve, 'wb')

    fname1_wdr = "1_" + "wdr" + ".wav"
    f1_wdr = open(fname1_wdr, 'wb')
    fname2_wdr = "2_" + "wdr" + ".wav"
    f2_wdr = open(fname2_wdr, 'wb')
    fname3_wdr = "3_" + "wdr" + ".wav"
    f3_wdr = open(fname3_wdr, 'wb')

    fname1_1005 = "1_" + "100,5" + ".wav"
    f1_1005 = open(fname1_1005, 'wb')
    fname2_1005 = "2_" + "100,5" + ".wav"
    f2_1005 = open(fname2_1005, 'wb')
    fname3_1005  = "3_" + "100,5" + ".wav"
    f3_1005 = open(fname3_1005, 'wb')

    fname1_ac = "1_" + "ac" + ".wav"
    f1_ac = open(fname1_ac, 'wb')
    fname2_ac = "2_" + "ac" + ".wav"
    f2_ac = open(fname2_ac, 'wb')
    fname3_ac = "3_" + "ac" + ".wav"
    f3_ac = open(fname3_ac, 'wb')

    fname1_big = "1_" + "big" + ".wav"
    f1_big = open(fname1_big, 'wb')
    fname2_big = "2_" + "big" + ".wav"
    f2_big = open(fname2_big, 'wb')
    fname3_big = "3_" + "big" + ".wav"
    f3_big = open(fname3_big, 'wb')

    fname1_bay1 = "1_" + "bay1" + ".wav"
    f1_bay1 = open(fname1_bay1, 'wb')
    fname2_bay1 = "2_" + "bay1" + ".wav"
    f2_bay1 = open(fname2_bay1, 'wb')
    fname3_bay1 = "3_" + "bay1" + ".wav"
    f3_bay1 = open(fname3_bay1, 'wb')


    offset = 2
    dauer = 10
    start = time.time()
    while True:
        try:
            audio_1lve = response.read(1024)
            audio_wdr = response2.read(1024)
            audio_1005 = response3.read(1024)
            audio_ac = response4.read(1024)
            audio_big = response5.read(1024)
            audio_bay1 = response6.read(1024)

            if start + dauer - offset < time.time() <= start + 2 * dauer - offset:  # 2. Block first offset Part
                f2_1lve.write(audio_1lve)
                f2_wdr.write(audio_wdr)
                f2_1005.write(audio_1005)
                f2_ac.write(audio_ac)
                f2_big.write(audio_big)
                f2_bay1.write(audio_bay1)
                sys.stdout.flush()

            if time.time() <= start + dauer:  # 1. Block
                f1_1lve.write(audio_1lve)
                f1_wdr.write(audio_wdr)
                f1_1005.write(audio_1005)
                f1_ac.write(audio_ac)
                f1_big.write(audio_big)
                f1_bay1.write(audio_bay1)
                sys.stdout.flush()
                sys.stdout.flush()
            else:
                break

        except Exception as e:
            print("Error " + str(e))


    f1_1lve.close()
    f1_wdr.close()
    f1_1005.close()
    f1_ac.close()
    f1_big.close()
    f1_bay1.close()
    sys.stdout.flush()
    Live1 = djv.recognize(FileRecognizer, fname1_1lve)
    if Live1 and Live1["confidence"] > 10:
        print(Live1)
    r1005 = djv.recognize(FileRecognizer, fname1_1005)
    if r1005 and r1005["confidence"] > 10:
        print(r1005)
    ac = djv.recognize(FileRecognizer, fname1_ac)
    if ac and ac["confidence"] > 10:
        print(ac)
    bigfm = djv.recognize(FileRecognizer, fname1_big)
    if bigfm and bigfm["confidence"] > 10:
        print(bigfm)
    wdr = djv.recognize(FileRecognizer, fname1_wdr)
    if wdr and wdr["confidence"] > 10:
        print(wdr)
    bay1 = djv.recognize(FileRecognizer, fname1_bay1)
    if bay1 and bay1["confidence"] > 10:
        print(bay1)
    i = 4

    while True:
        start = time.time()
        try:
            while time.time() - start <= dauer - offset:
                audio_1lve = response.read(1024)
                audio_wdr = response2.read(1024)
                audio_1005 = response3.read(1024)
                audio_ac = response4.read(1024)
                audio_big = response5.read(1024)
                audio_bay1 = response6.read(1024)

                if start <= time.time() <= start + dauer - offset:
                    f2_1lve.write(audio_1lve)
                    f2_wdr.write(audio_wdr)
                    f2_1005.write(audio_1005)
                    f2_ac.write(audio_ac)
                    f2_big.write(audio_big)
                    f2_bay1.write(audio_bay1)
                    sys.stdout.flush()
                if start + dauer - 2 * offset <= time.time() < start + dauer - offset:
                    f3_1lve.write(audio_1lve)
                    f3_wdr.write(audio_wdr)
                    f3_1005.write(audio_1005)
                    f3_ac.write(audio_ac)
                    f3_big.write(audio_big)
                    f3_bay1.write(audio_bay1)
                    sys.stdout.flush()

            f2_1lve.close()
            f2_wdr.close()
            f2_1005.close()
            f2_ac.close()
            f2_big.close()
            f2_bay1.close()
            sys.stdout.flush()
            Live1 = djv.recognize(FileRecognizer, fname2_1lve)
            if Live1 and Live1["confidence"] > 10:
                print(Live1)
            r1005 = djv.recognize(FileRecognizer, fname2_1005)
            if r1005 and r1005["confidence"] > 10:
                print(r1005)
            ac = djv.recognize(FileRecognizer, fname2_ac)
            if ac and ac["confidence"] > 10:
                print(ac)
            bigfm = djv.recognize(FileRecognizer, fname2_big)
            if bigfm and bigfm["confidence"] > 10:
                print(bigfm)
            wdr = djv.recognize(FileRecognizer, fname2_wdr)
            if wdr and wdr["confidence"] > 10:
                print(wdr)
            bay1 = djv.recognize(FileRecognizer, fname2_bay1)
            if bay1 and bay1["confidence"] > 10:
                print(bay1)
            fname2_1lve = str(i) + "_" + "1Live" + ".wav"
            fname2_big = str(i) + "_" + "big" + ".wav"
            fname2_1005 = str(i) + "_" + "1005" + ".wav"
            fname2_ac = str(i) + "_" + "ac" + ".wav"
            fname2_wdr = str(i) + "_" + "wdr" + ".wav"
            fname2_bay1 = str(i) + "_" + "bay1" + ".wav"
            f2_1lve = open(fname2_1lve, 'wb')
            f2_big = open(fname2_big, 'wb')
            f2_1005 = open(fname2_1005, 'wb')
            f2_ac = open(fname2_ac, 'wb')
            f2_wdr = open(fname2_wdr, 'wb')
            f2_bay1 = open(fname2_bay1, 'wb')
            sys.stdout.flush()
            i += 1

            while time.time() - start <= 2 * dauer - offset:
                audio_1lve = response.read(1024)
                audio_wdr = response2.read(1024)
                audio_1005 = response3.read(1024)
                audio_ac = response4.read(1024)
                audio_big = response5.read(1024)
                audio_bay1 = response6.read(1024)

                if start + dauer <= time.time() <= start + 2 * dauer - offset:
                    f3_1lve.write(audio_1lve)
                    f3_wdr.write(audio_wdr)
                    f3_1005.write(audio_1005)
                    f3_ac.write(audio_ac)
                    f3_big.write(audio_big)
                    f3_bay1.write(audio_bay1)
                    sys.stdout.flush()
                if start + 2 * dauer - 2 * offset <= time.time() < start + 2 * dauer - offset:
                    f2_1lve.write(audio_1lve)
                    f2_wdr.write(audio_wdr)
                    f2_1005.write(audio_1005)
                    f2_ac.write(audio_ac)
                    f2_big.write(audio_big)
                    f2_bay1.write(audio_bay1)
                    sys.stdout.flush()

            f3_1lve.close()
            f3_wdr.close()
            f3_1005.close()
            f3_ac.close()
            f3_big.close()
            f3_bay1.close()
            sys.stdout.flush()
            Live1 = djv.recognize(FileRecognizer, fname3_1lve)
            if Live1 and Live1["confidence"] > 10:
                print(Live1)
            r1005 = djv.recognize(FileRecognizer, fname3_1005)
            if r1005 and r1005["confidence"] > 10:
                print(r1005)
            ac = djv.recognize(FileRecognizer, fname3_ac)
            if ac and ac["confidence"] > 10:
                print(ac)
            bigfm = djv.recognize(FileRecognizer, fname3_big)
            if bigfm and bigfm["confidence"] > 10:
                print(bigfm)
            wdr = djv.recognize(FileRecognizer, fname3_wdr)
            if wdr and wdr["confidence"] > 10:
                print(wdr)
            bay1 = djv.recognize(FileRecognizer, fname3_bay1)
            if bay1 and bay1["confidence"] > 10:
                print(bay1)

            fname3_1lve = str(i) + "_" + "1Live" + ".wav"
            fname3_big = str(i) + "_" + "big" + ".wav"
            fname3_1005 = str(i) + "_" + "1005" + ".wav"
            fname3_ac = str(i) + "_" + "ac" + ".wav"
            fname3_wdr = str(i) + "_" + "wdr" + ".wav"
            fname3_bay1 = str(i) + "_" + "bay1" + ".wav"
            f3_1lve = open(fname3_1lve, 'wb')
            f3_big = open(fname3_big, 'wb')
            f3_1005 = open(fname3_1005, 'wb')
            f3_ac = open(fname3_ac, 'wb')
            f3_wdr = open(fname3_wdr, 'wb')
            f3_bay1 = open(fname3_bay1, 'wb')
            sys.stdout.flush()
            i += 1

        except Exception as e:
            print("Error " + str(e))


if __name__ == '__main__':
    # asyncio.run(StartClient())
    test()

    # pip install git+https://github.com/yunpengn/dejavu.git
    # pip install mysql
    # ffmpeg: https://phoenixnap.com/kb/ffmpeg-windows
