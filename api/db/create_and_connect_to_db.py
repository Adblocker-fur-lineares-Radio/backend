import os
from sqlalchemy import *
from dotenv import load_dotenv

from api.db.models import Base

# load your local .env file with db connection of format "postgresql+psycopg://username:password@hostname(ip):port"
load_dotenv()

CONNECTION_STRING = os.getenv('POSTGRESQL_DB_CONNECTION')
POOL_SIZE = int(os.getenv('POOL_SIZE'))
MAX_CONNECTIONS = int(os.getenv('MAX_CONNECTIONS'))


# connect to the db
# engine = create_engine(MY_ENV_VAR, echo=True)
engine = create_engine(CONNECTION_STRING, echo=False, pool_size=POOL_SIZE, max_overflow=MAX_CONNECTIONS - POOL_SIZE)
Base.metadata.create_all(engine)
engine.connect()
