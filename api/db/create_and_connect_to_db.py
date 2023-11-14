import os
from sqlalchemy import *
from dotenv import load_dotenv

from backend.api.db.models import Base

# load your local .env file with db connection of format "postgresql+psycopg://username:password@hostname(ip):port"
load_dotenv()

MY_ENV_VAR = os.getenv('POSTGRESQL_DB_CONNECTION')

# connect to the db
# engine = create_engine(MY_ENV_VAR, echo=True)
engine = create_engine(MY_ENV_VAR, echo=False)
Base.metadata.create_all(engine)
engine.connect()
