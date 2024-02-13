import json
import logging
from json import JSONDecodeError

from simple_websocket import ConnectionClosed

from src.api.search_request import search_request, search_update_request
from src.api.stream_request import stream_request
from src.db.database_functions import insert_new_connection, delete_connection_from_db
from src.db.db_helpers import NewTransaction
from src.error_handling.error_classes import Error
from src.logging_config import configure_logging

configure_logging()
logger = logging.getLogger("routes/endpoint.py")


def route_endpoint(client, connections):
    mapping = {
        'search_request': search_request,
        'search_update_request': search_update_request,
        'stream_request': stream_request,
    }

    with NewTransaction():
        connection_id = insert_new_connection()

    connections[connection_id] = client

    while True:
        try:
            raw = client.receive()
            data = json.loads(raw)

            callee = mapping[data['type']]
            callee(client, connection_id, data)

        except JSONDecodeError:
            msg = Error('Request body is not json').to_response()
            logger.error(f"Server sent error to client: {msg}")
            client.send(msg)

        except Error as e:
            client.send(e.to_response())

        except KeyError as e:
            msg = Error(f"Request body has incorrect json structure, couldn't find key '{e}'").to_response()
            logger.error(f"Server sent error to client: {msg}")
            client.send(msg)

        except ConnectionClosed:
            with NewTransaction():
                delete_connection_from_db(connection_id)
            del connections[connection_id]
            return

        except Exception as e:
            with NewTransaction():
                delete_connection_from_db(connection_id)
            logger.critical(f"########################\n#### Internal Server Error ####")
            del connections[connection_id]
            client.close()
            raise e
