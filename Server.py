import asyncio
import websockets
import json


def stream_guidance():
    return json.dumps({
        'type': 'stream_guidance',
        'radio': 'https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3?aggregator',
        'buffer': 0
    })


async def hello(websocket):
    name = await websocket.recv()
    print(f'Server Received: {name}')

    greeting = f'Hello {name}!'
    await websocket.send(greeting)
    print(f'Server Sent: {greeting}')

    streamRequest = await websocket.recv()
    print(f'Server Received: {streamRequest}')

    await websocket.send(stream_guidance())
    print(f'Server Sent: {stream_guidance()}')


async def main():
    async with websockets.serve(hello, "localhost", 1234):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
    # url1 = 'https://wdr-wdr2-rheinruhr.icecastssl.wdr.de/wdr/wdr2/rheinruhr/mp3/56/stream.mp3?aggregator=surfmusik-de&1697723004'
    # url2 = 'https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3?aggregator=radio-de'
