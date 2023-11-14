from flask import Flask
from flask_sock import Sock
import json
from json import JSONDecodeError
from simple_websocket import ConnectionClosed

from backend.api.notify_client import start_notifier
from stream_request import stream_request

from db.database_functions import insert_new_connection, commit, rollback
from search_request import search_request, search_update_request

app = Flask(__name__)
sock = Sock(app)

connections = {}


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True


def error(msg):
    return json.dumps({
        'type': 'error',
        'message': msg
    })


@sock.route('/api')
def api(client):
    mapping = {
        'search_request': search_request,
        'search_update_request': search_update_request,
        'stream_request': stream_request,
    }
    global connections
    connection_id = insert_new_connection()
    connections[connection_id] = client

    commit()

    while True:
        raw = "<Failed>"
        try:
            raw = client.receive()
            if is_json(raw):
                data = json.loads(raw)
                print(f"got request '{data['type']}': {raw}")
                mapping[data['type']](client, connection_id, data)
                commit()
            else:
                client.send(error("Request body is not json"))

        except JSONDecodeError:
            print("Error: Request body is not json")
            rollback()

        except KeyError:
            print(f"Error: Request body has incorrect json structure: {raw}")
            rollback()

        except ConnectionClosed:
            print("Connection closed")

        except Exception as e:
            # print(f"########################\n#### Internal Error ####\n{e}")
            rollback()
            client.close()
            raise e
            return


def testings():
    # Test Case
    class Dummy:
        def send(self, msg):
            print(f"Sending: {msg}")

    search_request(Dummy(), 30, {
        'type': 'search_request',
        'query': '1',
        'requested_updates': 5,
        'filter': {
            'ids': None,
            'without_ads': False
        }
    })


app.run()

notifier = start_notifier(connections)
notifier.join()

# close()
