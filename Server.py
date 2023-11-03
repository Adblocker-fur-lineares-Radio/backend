import asyncio
import websockets
import json


def stream_guidance_wdr():
    """
    Example of stream_guidance (Look Google Drive SeverAPI)
    @return: Json-String
    """
    return json.dumps({
        'type': 'stream_guidance',
        'radio': 'https://wdr-wdr2-rheinruhr.icecastssl.wdr.de/wdr/wdr2/rheinruhr/mp3/56/stream.mp3?aggregator'
                 '=surfmusik-de&1697723004',
        'buffer': 10
    })


def stream_guidance_1live():
    """
    2. Example of stream_guidance (Look Google Drive SeverAPI)
    @return: Json-String
    """
    return json.dumps({
        'type': 'stream_guidance',
        'radio': 'https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3?aggregator=radio-de',
        'buffer': 10
    })


async def hello(websocket):
    """
    Await request -> send Example -> permanently sending something to stable connection
    @param websocket: Server connection
    @return: None
    """
    streamRequest = await websocket.recv()
    print(f'Server Received: {streamRequest}')

    await websocket.send(stream_guidance_wdr())
    print(f'Server Sent: {stream_guidance_wdr()}')

    count = 0
    while True:
        await websocket.send("0")


async def main():
    async with websockets.serve(hello, "localhost", 1234):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
