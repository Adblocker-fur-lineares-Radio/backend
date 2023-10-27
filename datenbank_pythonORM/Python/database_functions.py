import database_ORM
from sqlalchemy.orm import sessionmaker

#create session with the db
Session = sessionmaker(bind=database_ORM.engine)
session = Session()

