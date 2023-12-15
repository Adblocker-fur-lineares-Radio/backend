from dejavu.recognize import FileRecognizer
from dejavu import Dejavu
import time
from urllib.request import urlopen
import os
import threading
from datetime import datetime


def test(Url, Offset, Dauer, FingerThreshold):
    config = {
        "database": {
            "host": "localhost",
            "user": "test123",
            "password": "test123",
            "database": "finger"
        },
    }
    djv = Dejavu(config)
    # djv.fingerprint_directory(r"..\OrginalAudio", [".wav"])

    offset = Offset
    dauer = Dauer
    fingerThreshold = FingerThreshold

    fname1 = "1_" + str(time.perf_counter())[2:] + ".wav"
    f1 = open(fname1, 'wb')
    fname2 = "2_" + str(time.perf_counter())[2:] + ".wav"
    f2 = open(fname2, 'wb')
    fname3 = "3_" + str(time.perf_counter())[2:] + ".wav"
    f3 = open(fname3, 'wb')

    response = urlopen(Url, timeout=10.0)
    start = time.time()
    while True:
        try:
            audio = response.read(1024)
            if time.time() <= start + dauer:
                f1.write(audio)
            else:
                break

            if start + dauer - offset <= time.time():
                f2.write(audio)
        except Exception as e:
            print("Error " + str(e))

    f1.close()
    try:
        if os.stat(fname1).st_size > 0:
            finger = djv.recognize(FileRecognizer, fname1)
            if finger and finger["confidence"] > fingerThreshold:
                print(datetime.now().strftime("%H:%M:%S") + ": " + str(finger))
                info = finger["confidence"].split("_")
                sender = info[0]
                Typ = info[1]
    except Exception as e:
        print("Error " + str(e))

    os.remove(fname1)
    i = 4
    while True:
        start = time.time()
        while time.time() - start <= dauer - offset:
            audio = response.read(1024)
            f2.write(audio)

            if start + dauer - 2 * offset < time.time():
                f3.write(audio)

        f2.close()
        try:
            if os.stat(fname2).st_size > 0:
                finger2 = djv.recognize(FileRecognizer, fname2)
                if finger2 and finger2["confidence"] > fingerThreshold:
                    print(datetime.now().strftime("%H:%M:%S") + ": " + str(finger2))
                    info = finger2["confidence"].split("_")
                    sender = info[0]
                    Typ = info[1]
        except Exception as e:
            print("Error " + str(e))

        #os.remove(fname2)
        #fname2 = str(i) + "_" + str(time.perf_counter())[2:] + ".wav"
        f2 = open(fname2, 'wb')
        i += 1

        while time.time() - start <= 2 * dauer - offset:
            audio = response.read(1024)
            f3.write(audio)

            if start + 2 * dauer - 2 * offset < time.time():
                f2.write(audio)

        f3.close()
        try:
            if os.stat(fname3).st_size > 0:
                finger3 = djv.recognize(FileRecognizer, fname3)
                if finger3 and finger3["confidence"] > fingerThreshold:
                    print(datetime.now().strftime("%H:%M:%S") + ": " + str(finger3))
                    info = finger3["confidence"].split("_")
                    sender = info[0]
                    Typ = info[1]
        except Exception as e:
            print("Error " + str(e))

        #os.remove(fname3)
        #fname3 = str(i) + "_" + str(time.perf_counter())[2:] + ".wav"
        f3 = open(fname3, 'wb')
        i += 1


def StartFinger():
    radios = ["https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3?aggregator=radio-de",
              "https://d121.rndfnk.com/ard/wdr/wdr2/rheinland/mp3/128/stream.mp3?cid=01FBS03TJ7KW307WSY5W0W4NYB&sid=2WfgdbO7GvnQL9AwD8vhvPZ9fs0&token=cz5XFBkPm158lD9VGL4JxM-2zzMfE_3qEd-sX_kdaAA&tvf=x6sCXJp9jRdkMTIxLnJuZGZuay5jb20",
              "https://d121.rndfnk.com/ard/br/br1/franken/mp3/128/stream.mp3?cid=01FCDXH5496KNWQ5HK18GG4HED&sid=2ZDBcNAOweP69799K4rCsFc3Jgw&token=AaURPm1j9atmzP6x_QnojyKUrDLXmpuME5vqVWX1ZI0&tvf=XJJyGEmbnhdkMTIxLnJuZGZuay5jb20",
              "https://stream.dashitradio.de/dashitradio/mp3-128/stream.mp3?ref",
              "https://antenneac--di--nacs-ais-lgc--06--cdn.cast.addradio.de/antenneac/live/mp3/high",
              "https://stream.bigfm.de/saarland/aac-128"]

    radios = ["https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3?aggregator=radio-de",
              "https://d121.rndfnk.com/ard/wdr/wdr2/rheinland/mp3/128/stream.mp3?cid=01FBS03TJ7KW307WSY5W0W4NYB&sid=2WfgdbO7GvnQL9AwD8vhvPZ9fs0&token=cz5XFBkPm158lD9VGL4JxM-2zzMfE_3qEd-sX_kdaAA&tvf=x6sCXJp9jRdkMTIxLnJuZGZuay5jb20",
              "https://d121.rndfnk.com/ard/br/br1/franken/mp3/128/stream.mp3?cid=01FCDXH5496KNWQ5HK18GG4HED&sid=2ZDBcNAOweP69799K4rCsFc3Jgw&token=AaURPm1j9atmzP6x_QnojyKUrDLXmpuME5vqVWX1ZI0&tvf=XJJyGEmbnhdkMTIxLnJuZGZuay5jb20"]

    threads = []
    for radio in radios:
        threads.append(threading.Thread(target=test, args=(radio, 2, 8, 15)))
        threads[-1].start()

    for t in threads:
        t.join()


if __name__ == '__main__':
    StartFinger()
