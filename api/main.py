from flask import Flask
from flask_sock import Sock
import json
from json import JSONDecodeError
from simple_websocket import ConnectionClosed

from api.Finger import start_fingerprint
from api.db.db_helpers import NewTransaction
from db.database_functions import insert_init, get_radio_by_query

from api.error_handling.error_classes import Error
from notify_client import start_notifier

from stream_request import stream_request

from db.database_functions import insert_new_connection, delete_all_connections_from_db
from db.database_functions import delete_connection_from_db
from search_request import search_request, search_update_request
import logging
from api.logging_config import configure_logging, csv_logging_setup

configure_logging()
logger = logging.getLogger("main.py")

logger.info("START")
csv_logging_setup()

with NewTransaction():
    insert_init()

configure_logging()
logger = logging.getLogger("main.py")

app = Flask(__name__)
sock = Sock(app)
log = logging.getLogger('werkzeug')
log.disabled = True

connections = {}

# deletes all residual connections from the db after server reboot
with NewTransaction():
    delete_all_connections_from_db()


# default page route specification
@app.route("/")
def index():
    with NewTransaction():
        radios = get_radio_by_query()
    radios = [f"""
        <tr>
            <td>{radio['name']}</td>
            <td>{radio['status_label']}</td>
            <td>{radio['currently_playing']}</td>
            <td>{radio['current_interpret']}</td>
        </tr>
    """ for radio in radios]
    radios = "\n".join(radios)

    html = f"""
    <html>
        <head>
            <title> Radio Adblocker </title>
            <meta charset='utf-8' />
            <style>
                table {{
                  font-family: arial, sans-serif;
                  border-collapse: collapse;
                  width: 100%;
                }}
                
                td, th {{
                  border: 1px solid #dddddd;
                  text-align: left;
                  padding: 8px;
                }}
                
                tr:nth-child(even) {{
                  background-color: #dddddd;
                }}
                </style>
        </head>
        <body>
            <p>Die API findet man unter /api</p>
            <table>
                <tr>
                    <th>Radio</th>
                    <th>Status</th>
                    <th>Songname</th>
                    <th>Interpret</th>
                </tr>
                {radios}
            </table>
            <a href="/">Aktualisieren</a><br />
        </body>
    </html>
    """
    return html


@app.route("/logs/adtimes/")
def logs_adtimes():
    with open("/logs/adtime.csv") as f:
        csv = f.read()
    rows = csv.split('\n')
    out = rows[-100:]
    out.reverse()
    nl = "\n"
    return f"""
    <html>
        <head>
            <title> Radio Adblocker </title>
            <meta charset='utf-8' />
        </head>
        <body>
            <a href="/logs/adtimes">Aktualisieren</a><br />
            <pre>{rows[0]}{nl.join(out)}</pre>
        </body>
    </html>
    """


@app.route("/logs/backend/")
def logs_backend():
    with open("/logs/backend.log") as f:
        text = f.read()
    rows = text.split('\n')
    out = rows[-100:]
    out.reverse()
    nl = "\n"
    return f"""
    <html>
        <head>
            <title> Radio Adblocker </title>
            <meta charset='utf-8' />
        </head>
        <body>
            <a href="/logs/backend">Aktualisieren</a><br />
            <pre>{nl.join(out)}</pre>
        </body>
    </html>
    """


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
threads = start_fingerprint(connections)

app.run(host="0.0.0.0")

notifier.join()
for thread in threads:
    thread.join()
