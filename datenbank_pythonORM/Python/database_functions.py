import os
from sqlalchemy import *
from sqlalchemy.orm import *
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from models import *
import create_and_connect_to_db

# create session with the db
Session = sessionmaker(bind=create_and_connect_to_db.engine)
session = Session()


# to access list elements, first loop through the rows, then access the db attribute, will return empty list if no
# query result
def get_radio_by_id(radio_id):
    """
    Queries DB for radio by specified id
    @param radio_id: the radio_id to be filtered by
    @return: the query result as a list
    """

    stmt = select(Radio).where(Radio.id == radio_id)
    return session.execute(stmt).all()


def get_radio_by_id_and_genre(radio_ids, genre_ids):
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
            RadioGenres.genre_id == genre_id).where(Radio.status_id != 1).limit(1)
        result = session.execute(stmt).all()

    result = []
    return result


def get_radio_by_connection(connection_id):
    """
    
    @param connection_id: 
    @return: a joined table of the radios and connections
    """
    stmt = select(Radio, Connections).join(ConnectionPreferredRadios,
                                           Radio.id == ConnectionPreferredRadios.radio_id).join(Connections,
                                                                                                ConnectionPreferredRadios.connection_id == Connections.id)
    result = session.execute(stmt).all()
    return result


def get_radio_by_query(search_query, search_without_ads):
    """
    Queries DB for radioname from query
    :param search_query: the query string to search a radio by
    :param search_without_ads: defines wether or not radio with ads should be returned
    :return: list of rows with radio entries (empty list if none found)
    """
    if search_without_ads:
        stmt = select(Radio).where(Radio.name.like("%" + search_query + "%")).where(Radio.status_id != 1)
    else:
        stmt = select(Radio).where(Radio.name.like("%" + search_query + "%"))

    return session.execute(stmt).all()


def get_preferred_radios(connection_id):
    """
    Queries DB for preferred Radios from a connection
    :param connection_id: specified connection
    :return: list of all preferred radios
    """
    stmt = select(ConnectionPreferredRadios).where(ConnectionPreferredRadios.connection_id == connection_id)
    return session.execute(stmt).all()


def get_preferred_genres(connection_id):
    """
    Queries DB for preferred Genres from a connection
    :param connection_id: specified connection
    :return: list of all preferred genres
    """
    stmt = select(ConnectionPreferredGenres).where(ConnectionPreferredGenres.connection_id == connection_id)
    return session.execute(stmt).all()


def get_search_favorites(connection_id):
    """
    Queries DB for search favorites from a Connection
    :param connection_id: specified connection
    :return: list of all search favorites
    """
    stmt = select(ConnectionSearchFavorites).where(ConnectionSearchFavorites.connection_id == connection_id)
    return session.execute(stmt).all()


def get_connection(connection_id):
    """
    Queries DB for specified connection
    :param connection_id: specifies connection
    :return: list of all connection attributes
    """
    stmt = select(Connections).where(Connections.id == connection_id)
    return session.execute(stmt).all()


def insert_new_connection(search_query, current_radio_id, search_without_ads, search_remaining_update, preference_music,
                          preference_talk, preference_news, preference_ad):
    """
    Inserts new connection into DB
    Adds a new connection entry to the db
    :param search_query:    specified search query
    :param current_radio_id: the currently listened to radio(can be null)
    :param search_without_ads:  specifies if search should only return radios without ads
    :param search_remaining_update: specifies how many updates should be sent
    :param preference_music: specifies if music is preferred
    :param preference_talk: specifies if talk is preferred
    :param preference_news: specifies if news is preferred
    :param preference_ad: specifies if ads are preferred
    :return: the inserted id

    """
    stmt = (insert(Connections).values(
        search_query=search_query,
        current_radio_id=current_radio_id,
        search_without_ads=search_without_ads,
        search_remaining_update=search_remaining_update,
        preference_music=preference_music,
        preference_talk=preference_talk,
        preference_news=preference_news,
        preference_ad=preference_ad
    ).returning(Connections.id))
    result = session.execute(stmt)
    connectionid = result.scalar()
    session.commit()
    return connectionid


def insert_into_connection_preferred_radios(radio_ids, connection_id):
    """
    Inserts the radio_ids and connection id in the connection_preferred_radios table,
    make sure to delete old values for connection before calling this again with same connection!!!
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
    make sure to delete old values for connection before calling this again with same connection!!!
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
    make sure to delete old values for connection before calling this again with same connection!!!
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


def update_search_remaining_updates(connection_id):
    stmt = (
        update(Connections).where(Connections.id == connection_id).where(
            Connections.search_remaining_update > 0).values(
            search_remaining_update=Connections.search_remaining_update - 1).returning(
            Connections.search_remaining_update)
    )
    result = session.execute(stmt)
    session.commit()
    search_remaining_updates = result.scalar()
    return search_remaining_updates


print(update_search_remaining_updates(1))
