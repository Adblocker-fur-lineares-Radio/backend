import os
from sqlalchemy import *
from dotenv import load_dotenv

from src.db.models import Base

# load your local .env file with db connection of format "postgresql+psycopg://username:password@hostname(ip):port"
load_dotenv()

CORE_POSTGRES_HOST = os.getenv('CORE_POSTGRES_HOST')
CORE_POSTGRES_USER = os.getenv('CORE_POSTGRES_USER')
CORE_POSTGRES_PASSWORD = os.getenv('CORE_POSTGRES_PASSWORD')
CORE_POSTGRES_DB = os.getenv('CORE_POSTGRES_DB')
POOL_SIZE = int(os.getenv('POOL_SIZE'))
MAX_CONNECTIONS = int(os.getenv('MAX_CONNECTIONS'))

CONNECTION_STRING = f"postgresql+psycopg://{CORE_POSTGRES_USER}:{CORE_POSTGRES_PASSWORD}@{CORE_POSTGRES_HOST}:5432/{CORE_POSTGRES_DB}"

# connect to the db
# engine = create_engine(MY_ENV_VAR, echo=True)
engine = create_engine(CONNECTION_STRING, echo=False, pool_size=POOL_SIZE, max_overflow=MAX_CONNECTIONS - POOL_SIZE)
Base.metadata.create_all(engine)
engine.connect()
