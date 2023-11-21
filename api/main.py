from flask import Flask
from flask_sock import Sock
import json
from json import JSONDecodeError
from simple_websocket import ConnectionClosed

from notify_client import start_notifier
from stream_request import stream_request

from db.database_functions import insert_new_connection, commit, rollback, \
    delete_all_connections_from_db
from db.database_functions import delete_connection_from_db
from search_request import search_request, search_update_request
from error import Error

app = Flask(__name__)
sock = Sock(app)

connections = {}

# deletes all residual connections from the db after server reboot

delete_all_connections_from_db()
commit()

# default page route specification
@app.route("/")
def index():
    return "<p>Hier wird nur die API unter /api gehostet \\o/</p>"


@sock.route('/api')
def api(client):
    mapping = {
        'search_request': search_request,
        'search_update_request': search_update_request,
        'stream_request': stream_request,
    }
    global connections
    connection_id = insert_new_connection()

    commit()
    connections[connection_id] = client

    while True:
        try:
            raw = client.receive()
            data = json.loads(raw)
            print(f"got request '{data['type']}': {raw}")
            mapping[data['type']](client, connection_id, data)
            commit()

        except JSONDecodeError:
            msg = Error('Request body is not json').to_response()
            print(f"Server sent: {msg}")
            client.send(msg)
            rollback()

        except Error as e:
            client.send(e.to_response())
            rollback()

        except KeyError as e:
            msg = Error(f"Request body has incorrect json structure, couldn't find key '{e}'").to_response()
            print(f"Server sent: {msg}")
            client.send(msg)
            rollback()

        except ConnectionClosed:
            # delete_connection_from_db(connection_id)
            # commit()
            print(f"Server closed connection to: {client}")
            return

        except Exception as e:
            delete_connection_from_db(connection_id)
            commit()
            print(f"########################\n#### Internal Server Error ####")
            rollback()
            client.close()
            raise e

notifier = start_notifier(connections)
app.run(host="0.0.0.0")



notifier.join()



# close()
