from flask import Flask
from flask_sock import Sock
import json
from json import JSONDecodeError
from search_request import search_request, search_update_request
from stream_request import stream_request
from websocket_api.periodic_test_update import start_test

app = Flask(__name__)
sock = Sock(app)

connections = {}


@sock.route('/api')
def api(client):
    mapping = {
        'search_request': search_request,
        'search_update_request': search_update_request,
        'stream_request': stream_request,
    }

    # TODO: get connection_id from db
    global connections
    connection_id = len(connections) + 1
    connections[connection_id] = client
    print(connections)

    while True:
        raw = "<Failed>"
        try:
            raw = client.receive()
            data = json.loads(raw)
            print(f"got request '{data['type']}'")
            mapping[data['type']](client, data)

        except JSONDecodeError:
            print("Error: Request body is not json")
        except KeyError:
            print(f"Error: Request body has incorrect json structure: {raw}")
        # except Exception as e:
        #     print(f"Internal Error: {e}")
        #     client.close()
        #     return


start_test(connections)
app.run()
