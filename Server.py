import asyncio
import websockets
import json

change = 0


def stream_guidance_wdr():
    return json.dumps({
        'type': 'stream_guidance',
        'radio': 'https://wdr-wdr2-rheinruhr.icecastssl.wdr.de/wdr/wdr2/rheinruhr/mp3/56/stream.mp3?aggregator=surfmusik-de&1697723004',
        'buffer': 0
    })


def stream_guidance_1live():
    return json.dumps({
        'type': 'stream_guidance',
        'radio': 'https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3?aggregator=radio-de',
        'buffer': 0
    })


async def hello(websocket):
    global change
    streamRequest = await websocket.recv()
    print(f'Server Received: {streamRequest}')

    await websocket.send(stream_guidance_wdr())
    print(f'Server Sent: {stream_guidance_wdr()}')

    count = 0
    while True:
        count = count + 1
        if count == 1000000:
            change = 1

        if change == 0:
            await websocket.send("0")
        else:
            await websocket.send(stream_guidance_1live())
            print(f'Server Sent: {stream_guidance_1live()}')
            change = 0


async def main():
    async with websockets.serve(hello, "localhost", 1234):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
    # url1 = 'https://wdr-wdr2-rheinruhr.icecastssl.wdr.de/wdr/wdr2/rheinruhr/mp3/56/stream.mp3?aggregator=surfmusik-de&1697723004'
    # url2 = 'https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3?aggregator=radio-de'
