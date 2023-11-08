import os
from sqlalchemy import *
from sqlalchemy.orm import *
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from models import *

# load your local .env file with db connection of format "postgresql+psycopg://username:password@hostname(ip):port"
load_dotenv()

MY_ENV_VAR = os.getenv('POSTGRESQL_DB_CONNECTION')

# connect to the db
engine = create_engine(MY_ENV_VAR, echo=True)
Base.metadata.create_all(engine)
engine.connect()
