from flask import Flask
from flask_sock import Sock
import json
from json import JSONDecodeError
from simple_websocket import ConnectionClosed

from api.db.db_helpers import NewTransaction
from notify_client import start_notifier
from stream_request import stream_request

from db.database_functions import insert_new_connection, delete_all_connections_from_db
from db.database_functions import delete_connection_from_db, insert_init
from search_request import search_request, search_update_request
from error import Error
import logging
from api.logging_config import configure_logging

configure_logging()
logger = logging.getLogger("main.py")

logger.info("START")

app = Flask(__name__)
sock = Sock(app)

connections = {}

with NewTransaction():
    insert_init()

# deletes all residual connections from the db after server reboot
with NewTransaction():
    delete_all_connections_from_db()


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

    with NewTransaction():
        connection_id = insert_new_connection()

    connections[connection_id] = client

    while True:
        try:
            raw = client.receive()
            data = json.loads(raw)
            logger.info(f"got request '{data['type']}': {raw}")

            callee = mapping[data['type']]
            callee(client, connection_id, data)

        except JSONDecodeError:
            msg = Error('Request body is not json').to_response()
            logger.info(f"Server sent: {msg}")
            client.send(msg)

        except Error as e:
            client.send(e.to_response())

        except KeyError as e:
            msg = Error(f"Request body has incorrect json structure, couldn't find key '{e}'").to_response()
            logger.error(f"Server sent: {msg}")
            client.send(msg)

        except ConnectionClosed:
            with NewTransaction():
                delete_connection_from_db(connection_id)
            logger.error(f"Server closed connection to: {client}")
            del connections[connection_id]
            return

        except Exception as e:
            with NewTransaction():
                delete_connection_from_db(connection_id)
            logger.critical(f"########################\n#### Internal Server Error ####")
            del connections[connection_id]
            client.close()
            raise e


notifier = start_notifier(connections)
app.run(host="0.0.0.0")

notifier.join()
