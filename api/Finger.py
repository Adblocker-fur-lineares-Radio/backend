from dejavu.recognize import FileRecognizer
from dejavu import Dejavu
import time
import sys
from urllib.request import urlopen
import os
import threading


def test(Url, Offset, Dauer , FingerThreshold):
    config = {
        "database": {
            "host": "localhost",
            "user": "test123",
            "password": "test123",
            "database": "finger"
        },
    }
    djv = Dejavu(config)
    #djv.fingerprint_directory(r"..\OrginalAudio", [".wav"])

    offset = Offset
    dauer = Dauer
    fingerThreshold = FingerThreshold

    fname1 = "1_" + str(time.perf_counter())[2:] + ".wav"
    f1 = open(fname1, 'wb')
    fname2= "2_" + str(time.perf_counter())[2:] + ".wav"
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
                sys.stdout.flush()
            else:
                break

            if start + dauer - offset <= time.time():
                f2.write(audio)
                sys.stdout.flush()
        except Exception as e:
            print("Error " + str(e))

    sys.stdout.flush()
    f1.close()

    finger = djv.recognize(FileRecognizer, fname1)
    if finger and finger["confidence"] > fingerThreshold:
        print(finger)
    os.remove(fname1)

    i = 4
    while True:
        start = time.time()
        try:
            while time.time() - start <= dauer - offset:
                audio = response.read(1024)
                f2.write(audio)
                sys.stdout.flush()

                if start + dauer - 2 * offset < time.time():
                    f3.write(audio)
                    sys.stdout.flush()

            sys.stdout.flush()
            f2.close()

            finger2 = djv.recognize(FileRecognizer, fname2)
            if finger2 and finger2["confidence"] > fingerThreshold:
                print(finger2)

            os.remove(fname2)
            fname2 = str(i) + "_" + str(time.perf_counter())[2:] + ".wav"
            f2 = open(fname2, 'wb')
            sys.stdout.flush()
            i += 1

            while time.time() - start <= 2 * dauer - offset:
                audio = response.read(1024)
                f3.write(audio)
                sys.stdout.flush()

                if start + 2 * dauer - 2 * offset < time.time():
                    f2.write(audio)
                    sys.stdout.flush()

            sys.stdout.flush()
            f3.close()
            finger3 = djv.recognize(FileRecognizer, fname3)
            if finger3 and finger3["confidence"] > fingerThreshold:
                print(finger3)

            os.remove(fname3)
            fname3 = str(i) + "_" + str(time.perf_counter())[2:] + ".wav"
            f3 = open(fname3, 'wb')
            sys.stdout.flush()
            i += 1

        except Exception as e:
            print("Error " + str(e))


if __name__ == '__main__':
    #test("https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3?aggregator=radio-de", 2, 10, 10)
    x = threading.Thread(target=test, args=("https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3?aggregator=radio-de", 2, 10, 10))
    x.start()

    y = threading.Thread(target=test, args=("https://d121.rndfnk.com/ard/wdr/wdr2/rheinland/mp3/128/stream.mp3?cid=01FBS03TJ7KW307WSY5W0W4NYB&sid=2WfgdbO7GvnQL9AwD8vhvPZ9fs0&token=cz5XFBkPm158lD9VGL4JxM-2zzMfE_3qEd-sX_kdaAA&tvf=x6sCXJp9jRdkMTIxLnJuZGZuay5jb20", 2, 10, 10))
    y.start()

    z = threading.Thread(target=test, args=("https://d121.rndfnk.com/ard/br/br1/franken/mp3/128/stream.mp3?cid=01FCDXH5496KNWQ5HK18GG4HED&sid=2ZDBcNAOweP69799K4rCsFc3Jgw&token=AaURPm1j9atmzP6x_QnojyKUrDLXmpuME5vqVWX1ZI0&tvf=XJJyGEmbnhdkMTIxLnJuZGZuay5jb20", 2, 10, 10))
    z.start()

    z.join()
    y.join()
    x.join()



