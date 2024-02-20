import logging

from flask import Flask
from flask_sock import Sock

from db.database_functions import delete_all_connections_from_db
from src.api.routes.endpoint import route_endpoint
from src.api.routes.index import route_radio_list
from src.api.routes.logs import route_adtime_logs, route_backend_logs
from src.backend.fingerprinting import start_fingerprint
from src.backend.metadata_updater import start_notifier
from src.db.db_helpers import NewTransaction
from src.db.inserts.initialize import insert_init
from src.logging_config import configure_logging, csv_logging_setup

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
    return route_radio_list()


@app.route("/logs/adtimes/")
def logs_adtimes():
    return route_adtime_logs()


@app.route("/logs/backend/")
def logs_backend():
    return route_backend_logs()


@sock.route('/api')
def api(client):
    return route_endpoint(client, connections)


notifier = start_notifier(connections)
threads = start_fingerprint(connections)

app.run(host="0.0.0.0")

notifier.join()
for thread in threads:
    thread.join()
