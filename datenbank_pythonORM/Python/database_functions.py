import psycopg
import os
from sqlalchemy import *
from sqlalchemy.orm import *
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from models import *
import array
from inspect import getmembers
from pprint import pprint

# load your local .env file with db connection of format "postgresql+psycopg://username:password@hostname(ip):port"
load_dotenv()

MY_ENV_VAR = os.getenv('POSTGRESQL_DB_CONNECTION')

# connect to the db
engine = create_engine(MY_ENV_VAR, echo=True)
engine.connect()

# create session with the db
Session = sessionmaker(bind=engine)
session = Session()


# to access list elements, first loop through the rows, then access the db attribute, will return empty list if no
# query result
def search_radio_by_id(radio_id):
    """
    Looks for radio with specified id in db
    @param radio_id: the radio_id to be filtered by
    @return: the query result as a list
    """

    stmt = select(Radio).where(Radio.id == radio_id)
    result = session.execute(stmt).all()


def search_radio_by_id_and_genre(radio_ids, genre_ids):
    """
    Tries to match a radio from the preferred list to a radio that does not play ads right now,
    if none exist, try to find a radio that matches with the most preferred genre, if none exists
    return an empty list
    @param radio_ids: array with preferred radios
    @param genre_ids: array with preferred genres
    @return: the radio that best matches the query
    """
    for radio_id in radio_ids:
        stmt = select(Radio).where(Radio.id == radio_id).where(Radio.status_id != 1)
        result = session.execute(stmt).all()
        if len(result) != 0:
            return result

    for genre_id in genre_ids:
        stmt = select(Radio, RadioGenres.genre_id).join(RadioGenres, Radio.id == RadioGenres.radio_id).where(
            RadioGenres.genre_id == genre_id).where(Radio.status_id != 1)
        result = session.execute(stmt).all()
        if len(result) != 0:
            return result[0]

    result = []
    return result


def insert_into_connection_preferred_radios(radio_ids, connection_id):
    """
    Inserts the radio_ids and connection id in the connection_preferred_radios table,
    make sure to delete old values for connection before calling this again!!!
    @param radio_ids: array with preferred radios
    @param connection_id: the corresponding connection id
    @return: -
    """

    for radio_id in radio_ids:
        session.execute(insert(ConnectionPreferredRadios), [{"radio_id": radio_id, "connection_id": connection_id}])
    session.commit()


def insert_into_connection_search_favorites(radio_ids, connection_id):
    """
    Inserts the radio_ids and connection id in the connection_search_favorites table,
    make sure to delete old values for connection before calling this again!!!
    @param radio_ids: array with preferred radios
    @param connection_id: the corresponding connection id
    @return: -
    """
    for radio_id in radio_ids:
        session.execute(insert(ConnectionSearchFavorites), [{"radio_id": radio_id, "connection_id": connection_id}])
    session.commit()


def insert_into_connection_preferred_genres(genre_ids, connection_id):
    """
    Inserts the genre_ids and connection id in the connection_preferred_genres table,
    make sure to delete old values for connection before calling this again!!!
    @param genre_ids: array with preferred genres
    @param connection_id: the corresponding connection id
    @return: -
    """
    for genre_id in genre_ids:
        session.execute(insert(ConnectionPreferredGenres), [{"genre_id": genre_id, "connection_id": connection_id}])
    session.commit()


def delete_connection_from_db(connection_id):
    """
    Removes all entries from "connections", "connection_search_favorites", "connection_preferred_radios",
    "connection_preferred_genres", entries with specified connection_od
    @param connection_id: the connection to be delete
    @return -

    """
    stmt = delete(ConnectionPreferredGenres).where(ConnectionPreferredGenres.connection_id == connection_id)
    session.execute(stmt)
    stmt = delete(ConnectionPreferredRadios).where(ConnectionPreferredRadios.connection_id == connection_id)
    session.execute(stmt)
    stmt = delete(ConnectionSearchFavorites).where(ConnectionSearchFavorites.connection_id == connection_id)
    session.execute(stmt)
    stmt = delete(Connections).where(Connections.id == connection_id)
    session.execute(stmt)
    session.commit()


delete_connection_from_db(1)