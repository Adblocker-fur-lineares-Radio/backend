import asyncio
import websockets
import json
import logging
from api.logging_config import configure_logging

configure_logging()

logger = logging.getLogger("Server.py")


def stream_guidance_wdr():
    """
    Example of stream_guidance (Look Google Drive SeverAPI)
    @return: Json-String
    """
    return json.dumps({
        'type': 'stream_guidance',
        'radio': 'https://wdr-wdr2-rheinruhr.icecastssl.wdr.de/wdr/wdr2/rheinruhr/mp3/56/stream.mp3?aggregator'
                 '=surfmusik-de&1697723004',
        'buffer': 1
    })


def stream_guidance_1live():
    """
    2. Example of stream_guidance (Look Google Drive SeverAPI)
    @return: Json-String
    """
    return json.dumps({
        'type': 'stream_guidance',
        'radio': 'https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3?aggregator=radio-de',
        'buffer': 1
    })


def switch_to_test():
    """
    2. Example of switch_to
    @return: Json-String
    """
    return json.dumps({
        'type': 'radio_switch_event',
        'switch_to': 'https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3?aggregator=radio-de',
        'buffer': 1
    })


def switch_to_test2():
    """
    2. Example of switch_to
    @return: Json-String
    """
    return json.dumps({
        'type': 'radio_switch_event',
        'switch_to': 'https://wdr-wdr2-rheinruhr.icecastssl.wdr.de/wdr/wdr2/rheinruhr/mp3/56/stream.mp3?aggregator'
                     '=surfmusik-de&1697723004',
        'buffer': 1
    })


async def hello(websocket):
    """
    Await request -> send Example -> permanently sending something to stable connection
    @param websocket: Server connection
    @return: None
    """
    streamRequest = await websocket.recv()
    logger.info(f'Server Received: {streamRequest}')

    await websocket.send(stream_guidance_wdr())
    logger.info(f'Server Sent: {stream_guidance_wdr()}')

    await asyncio.sleep(5)

    await websocket.send(switch_to_test())
    logger.info(f'Server Sent: {switch_to_test()}')

    await asyncio.sleep(10)

    await websocket.send(switch_to_test2())
    logger.info(f'Server Sent: {switch_to_test2()}')


async def main():
    async with websockets.serve(hello, 'localhost', 1234):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
