from datetime import datetime

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.orm import sessionmaker
from api.db import create_and_connect_to_db
from api.db.models import Radios, Connections, ConnectionSearchFavorites, ConnectionPreferredRadios, \
    ConnectionPreferredGenres, RadioGenres, RadioAdTime

# create session with the db
Session = sessionmaker(bind=create_and_connect_to_db.engine)
session = Session()

STATUS = {
    "ad": 1,
    "music": 2,
    "news": 3,
    "nothing": 4,
    "talk": 4  # TODO: maybe add a status for that one
}


def commit():
    """
    Commits the currently executed session statements
    @return: -
    """
    session.commit()


def rollback():
    """
    Rolls the currently executed session statements back
    @return: -
    """
    session.rollback()


def close():
    """
    Closes the current session
    @return: -
    """
    session.close()


def serializeRow(row):
    """
    Helper function to prepare db row in json format
    @param row: the row or rows returned from a SQLAlchemy Query
    @return: The serialized value and key of a row
    """
    return {c.key: getattr(row, c.key) for c in inspect(row).mapper.column_attrs}


def serializeRows(rows):
    """
    Helper function to prepare multiple db rows in json format
    @param rows: the row or rows returned from a SQLAlchemy Query
    @return: The serialized value and key of multiple rows
    """
    return [serializeRow(r[0]) for r in rows]


def serialize(rowOrRows):
    """
    Serializes the input with serializeRow or serializeRows depending on input
    @param rowOrRows: the row or rows returned from a SQLAlchemy Query
    @return: the serialized row
    """
    if isinstance(rowOrRows, list):
        return serializeRows(rowOrRows)
    elif rowOrRows is None:
        return None
    else:
        return serializeRow(rowOrRows)


def untuple(rows):
    """
    Untuples the passed row
    @param rows: the row or rows returned from a SQLAlchemy Query
    @return: returns the first element of the tuple of rows
    """
    return [r[0] for r in rows]


def first(stmt):
    """
    Checks if SQLAlchemy Query result exists, and returns the first result if it does
    @param stmt: The SQLAlchemy Query
    @return: the first result of the SQLAlchemy Query, or None
    """
    result = session.execute(stmt).first()
    return None if result is None else result[0]


def all(stmt):
    """
    Prepares the outcome of an SQLAlchemy  Query by untupling it
    @param stmt: the SQLAlchemy Query
    @return: the untupled results as list of rows
    """
    result = session.execute(stmt).all()
    return untuple(result)


# usage:
# with transaction():
#     code that runs in a transaction
def transaction():
    """
    Begins the PostgreSQL transaction
    @return: starts the transaction
    """
    return session.begin()


# to access list elements, first loop through the rows, then access the db attribute, will return empty list if no
# query result
def get_radio_by_id(radio_id):
    """
    Queries DB for radio by specified id
    @param radio_id: the radio_id to be filtered by
    @return: the Query result as a row
    """

    stmt = select(Radios).where(Radios.id == radio_id)
    return first(stmt)


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
        stmt = select(Radios).where(Radios.id == radio_id).where(Radios.status_id != STATUS["ad"])
        result = all(stmt)
        if len(result) != 0:
            return result

    for genre_id in genre_ids:
        stmt = select(Radios, RadioGenres.genre_id).join(RadioGenres, Radios.id == RadioGenres.radio_id).where(
            RadioGenres.genre_id == genre_id).where(Radios.status_id != STATUS["ad"]).limit(1)
        result = all(stmt)

    result = []
    return result


def get_radio_by_connection(connection_id):
    """
    Matches the preferred Radios to the specified connection
    @param connection_id: 
    @return: a joined table of the radios and connections
    """
    stmt = select(Radios, Connections).join(ConnectionPreferredRadios,
                                            Radios.id == ConnectionPreferredRadios.radio_id).join(Connections,
                                                                                                  ConnectionPreferredRadios.connection_id == Connections.id)
    return first(stmt)


def get_radio_by_query(search_query=None, search_without_ads=None, ids=None):
    """
    Queries DB for radioname from query
    @param search_query: the query string to search a radio by. Leave blank to search all
    @param search_without_ads: defines wether or not radio with ads should be returned
    @param ids: the favorites to filter for. Leave blank to search all
    @return: list of rows with radio entries (empty list if none found)
    """

    stmt = select(Radios)

    if search_query:
        stmt = stmt.where(Radios.name.like("%" + search_query + "%"))

    if search_without_ads:
        stmt = stmt.where(Radios.status_id != STATUS["ad"])

    if ids:
        stmt = stmt.where(Radios.id.in_(ids))

    return all(stmt)


def get_connections_by_radio_and_remaining_updates(radio_id):
    """
    Queries DB for a connection with the current radio
    equal to the specified radio_id that has more than 0 remaining updates
    @param radio_id: the radio_id to be searched for
    @return: the connections as an untupled list of rows
    """
    stmt = (select(Connections)
            .where(Connections.current_radio_id == radio_id)
            .where(Connections.search_remaining_update > 0))
    return all(stmt)


'''
def get_connections_by_radio(radio_id):
    """
    Queries DB for
    @param radio_id:
    @return:
    """
    stmt = (select(Connections)
            .where(Connections.current_radio_id == radio_id)
            .where(Connections.search_remaining_update > 0))
    return all(stmt)
'''


def get_preferred_radios(connection_id):
    """
    Queries DB for preferred Radios from a connection
    :param connection_id: specified connection
    :return: list of all preferred radios
    """
    stmt = select(ConnectionPreferredRadios).where(ConnectionPreferredRadios.connection_id == connection_id)
    return all(stmt)


def get_connections_by_radio(radio_id):
    """
    Queries DB for a connection where the current radio equals the parameter radio_id and the state is allowed
    @param radio_id: the primary key to be searched for
    @return: the connection as a list of rows
    """
    stmt = (select(Connections, Radios)
            .select_from(Radios)
            .join(Connections.current_radio)
            .where(Connections.current_radio_id == radio_id))

    result = session.execute(stmt).all()
    return [(row[0], row[1].status_id in helper_get_allowed_states(row[0])) for row in result]


def helper_get_allowed_states(connection):
    """
    Helper function to limit returned rows to ones with only allowed states
    @param connection: the connection object mapping the DB table connections
    @return: a list of allowed states
    """
    allowed_states = []
    if connection.preference_music:
        allowed_states.append(STATUS["music"])
    if connection.preference_talk:
        allowed_states.append(STATUS["talk"])
    if connection.preference_news:
        allowed_states.append(STATUS["news"])
    if connection.preference_ad:
        allowed_states.append(STATUS["ad"])
    return allowed_states


def switch_to_working_radio(connection_id):
    """
    Selects a radio for the connection that fits all filtered requirements
    @param connection_id: the specified connection that should switch the radio
    @return: the radio_id of the new radio, or None
    """
    connection = get_connection(connection_id)
    allowed_states = helper_get_allowed_states(connection)

    stmt = (select(Radios)
            .select_from(Connections)
            .join(Connections.preferred_radios)
            .where(Connections.id == connection_id)
            .where(Radios.status_id.in_(allowed_states)))

    radio = first(stmt)

    if radio is not None:
        # TODO: add genre fallback
        pass

    if radio is not None:
        # select 'random' radio
        # TODO: give user status about that it doesn't not a preferred radio
        stmt = (select(Radios)
                .where(Radios.status_id.in_(allowed_states)))
        radio = first(stmt)

    if radio:
        stmt = (update(Connections)
                .where(Connections.id == connection_id)
                .values(current_radio_id=radio.id))
        session.execute(stmt)
        return radio.id

    if not radio:
        # there's no radio to go to
        # TODO: notify user about: there's no option to switch to
        pass

    return None


def get_preferred_genres(connection_id):
    """
    Queries DB for preferred Genres from a connection
    :param connection_id: specified connection
    :return: list of all preferred genres
    """
    stmt = select(ConnectionPreferredGenres).where(ConnectionPreferredGenres.connection_id == connection_id)
    return all(stmt)


def get_connection_favorites(connection_id):
    """
    Queries DB for search favorites from a Connection
    :param connection_id: specified connection
    :return: list of all search favorites
    """
    stmt = select(ConnectionSearchFavorites).where(ConnectionSearchFavorites.connection_id == connection_id)
    return all(stmt)


def get_connection(connection_id):
    """
    Queries DB for specified connection
    :param connection_id: specifies connection
    :return: list of all connection attributes
    """
    stmt = select(Connections).where(Connections.id == connection_id)
    return first(stmt)


def insert_new_connection(search_query=None, current_radio_id=None, search_without_ads=None,
                          search_remaining_update=0, preference_music=None,
                          preference_talk=None, preference_news=None, preference_ad=None):
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
    return result.scalar()


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


def delete_connection_from_db(connection_id):
    """
    Removes all entries from "connections", "connection_search_favorites", "connection_preferred_radios",
    "connection_preferred_genres", entries with specified connection_od
    @param connection_id: the connection to be delete
    @return -

    """

    stmt = delete(Connections).where(Connections.id == connection_id)
    session.execute(stmt)


def delete_all_connections_from_db():
    """
    Deletes all connections from the DB, used on Serverstart/crash
    @return: -
    """
    session.execute(text("""TRUNCATE TABLE connections CASCADE"""))


def update_search_remaining_updates(connection_id, value=None):
    """
    Updates the DB attribute search_remaining_update
    @param connection_id: the corresponding connection_id
    @param value: amount of updates that should be remaining. If left blank, it decrements by one
    @return: the amount of remaining updates or 0
    """
    stmt = update(Connections).where(Connections.id == connection_id)
    if value:
        stmt = stmt.values(search_remaining_update=value).returning(Connections.search_remaining_update)
    else:
        stmt = stmt.where(
            Connections.search_remaining_update > 0).values(
            search_remaining_update=Connections.search_remaining_update - 1).returning(
            Connections.search_remaining_update)
    result = session.execute(stmt)
    search_remaining_updates = result.scalar()
    return search_remaining_updates or 0


def update_search_request_for_connection(connection_id, search_query=None, without_ads=False, ids=None,
                                         requested_updates=None):
    """
    Updates the DB table connections
    @param connection_id: the specified connection
    @param search_query: the passed search query
    @param without_ads: the passed preference on ads
    @param ids: the connection_search_favorite radio ids
    @param requested_updates: the passed amount of requested updates
    @return: -
    """
    stmt = (update(Connections)
            .where(Connections.id == connection_id)
            .values(search_query=search_query,
                    search_without_ads=without_ads,
                    search_remaining_update=requested_updates))
    session.execute(stmt)

    stmt = (delete(ConnectionSearchFavorites)
            .where(ConnectionSearchFavorites.connection_id == connection_id))
    session.execute(stmt)

    if ids:
        favorites = [{"radio_id": i, "connection_id": connection_id} for i in (ids or [])]
        stmt = insert(ConnectionSearchFavorites).values(favorites)
        session.execute(stmt)


def update_preferences_for_connection(connection_id, preferred_radios=None, preferred_genres=None, preference_ad=None,
                                      preference_talk=None, preference_news=None, preference_music=None):
    """
    Updates the DB for user preferences for the specified connection
    @param connection_id: the specified connection
    @param preferred_radios: the users preferred radios
    @param preferred_genres: the users preferred genres
    @param preference_ad: the users preference on ads
    @param preference_talk: the users preference on talk
    @param preference_news: the users preference on news
    @param preference_music: the users preference on music
    @return: -
    """
    stmt = (update(Connections)
            .where(Connections.id == connection_id)
            .values(preference_talk=preference_talk,
                    preference_news=preference_news,
                    preference_music=preference_music,
                    preference_ad=preference_ad))
    session.execute(stmt)

    stmt = delete(ConnectionPreferredRadios).where(ConnectionPreferredRadios.connection_id == connection_id)
    session.execute(stmt)

    if isinstance(preferred_radios, list) and len(preferred_radios) > 0:
        stmt = insert(ConnectionPreferredRadios).values([
            {"connection_id": connection_id, "radio_id": i}
            for i in preferred_radios
        ])
        session.execute(stmt)

    if isinstance(preferred_genres, list) and len(preferred_genres) > 0:
        stmt = insert(ConnectionPreferredGenres).values([
            {"connection_id": connection_id, "genre_id": i}
            for i in preferred_genres
        ])
        session.execute(stmt)

    stmt = delete(ConnectionPreferredGenres).where(ConnectionPreferredGenres.connection_id == connection_id)
    session.execute(stmt)


def xor_(q1, q2):
    """
    Computes the logical xor of 2 SQLAlchemy Statements
    @param q1: Querystatement 1
    @param q2: Querystatement 2
    @return: the logical result
    """
    return or_(
        and_(not_(q1), q2),
        and_(not_(q2), q1)
    )


def get_radios_that_need_switch_by_time_and_update():
    """
    Querys the DB for the radios that need to be switched away from
    @return: the list of rows of radios
    """
    now = func.now()

    # if inDerZeitVonWerbung xor status == 'werbung'

    hour_check = func.date_part('hour', now).between(RadioAdTime.ad_transmission_start, RadioAdTime.ad_transmission_end)
    minute_check = (func.date_part('minute', now).between(RadioAdTime.ad_start_time - 1, RadioAdTime.ad_end_time + 1))

    ad_check = and_(hour_check, minute_check)
    current_status_is_ad = Radios.status_id == STATUS['ad']

    stmt = (select(Radios).join(RadioAdTime, RadioAdTime.radio_id == Radios.id)
    .where(xor_(
        ad_check,
        not_(current_status_is_ad))
    ))

    select_ids = select(Radios.id).join(RadioAdTime, RadioAdTime.radio_id == Radios.id)
    select_ads = select_ids.where(ad_check)
    select_not_ads = select_ids.where(not_(ad_check))

    stmt2 = update(Radios).where(Radios.id.in_(select_ads)).values(status_id=STATUS['ad'])
    stmt3 = update(Radios).where(Radios.id.in_(select_not_ads)).values(status_id=STATUS['music'])

    session.execute(stmt2)
    session.execute(stmt3)

    stmt4 = select(func.min(RadioAdTime.ad_start_time)).where(RadioAdTime.ad_start_time > func.date_part('minute', now))
    next_event = untuple(session.execute(stmt4))
    if next_event[0] is None:
        stmt5 = select(func.min(RadioAdTime.ad_start_time)).where(
            RadioAdTime.ad_start_time <= func.date_part('minute', now))
        next_event = untuple(session.execute(stmt5))

    return [all(stmt), next_event[0]]
