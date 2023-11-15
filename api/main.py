from flask import Flask
from flask_sock import Sock
import json
from json import JSONDecodeError
from simple_websocket import ConnectionClosed

from notify_client import start_notifier
from stream_request import stream_request

from db.database_functions import insert_new_connection, commit, rollback, delete_connection_from_db, \
    delete_all_connections_from_db
from search_request import search_request, search_update_request

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


# tries to load json file if it has the correct format
def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True


# helper function to send an error message
def error(msg):
    return json.dumps({
        'type': 'error',
        'message': msg
    })

# /api page route specification
# is responsible to send errors and
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
            if is_json(raw):  # FIXME: don't parse `raw` twice
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
            delete_connection_from_db(connection_id)
            commit()
            print("Connection closed")
            return

        except Exception as e:
            delete_connection_from_db(connection_id)
            commit()
            print(f"########################\n#### Internal Server Error ####")
            rollback()
            client.close()
            raise e


app.run(host="0.0.0.0")

notifier = start_notifier(connections)
notifier.join()

# close()
