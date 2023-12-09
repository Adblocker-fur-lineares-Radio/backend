from datetime import datetime

from sqlalchemy import *
from api.db.db_helpers import STATUS, helper_get_allowed_states
from api.db.models import Radios, Connections, ConnectionSearchFavorites, ConnectionPreferredRadios, \
    ConnectionPreferredGenres, RadioAdTime, RadioMetadata


# to access list elements, first loop through the rows, then access the db attribute, will return empty list if no
# query result
def get_radio_by_id(session, radio_id):
    """
    Queries DB for radio by specified id
    :param session: the session to use
    :param radio_id: the radio_id to be filtered by
    :return: the Query result as a row
    """

    stmt = select(Radios).where(Radios.id == radio_id)
    return session.first(stmt)


def get_radio_by_connection(session, connection_id):
    """
    Matches the preferred Radios to the specified connection
    @param connection_id: 
    @return: a joined table of the radios and connections
    """
    stmt = (select(Radios, Connections)
            .join(ConnectionPreferredRadios, Radios.id == ConnectionPreferredRadios.radio_id)
            .join(Connections, ConnectionPreferredRadios.connection_id == connection_id))
    return session.first(stmt)


def get_all_radios(session):
    """
    Queries DB for all radios
    @return: list of rows with radio entries (empty list if none found)
    """

    stmt = select(Radios)
    return session.all(stmt)


def radios_existing(session, radio_ids):
    """
    Checks given list of ids for their existance in the db
    @param radio_ids list of radio ids
    @return: true if every id exists
    """

    stmt = select(func.count()).select_from(Radios).where(Radios.id.in_(radio_ids))
    count = session.scalar(stmt)
    return count == len(radio_ids)


def get_radio_by_query(session, search_query=None, search_without_ads=None, ids=None):
    """
    Queries DB for radioname from query
    @param search_query: the query string to search a radio by. Leave blank to search all
    @param search_without_ads: defines whether radio with ads should be returned
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

    return session.all(stmt)


def get_connections_by_remaining_updates(session):
    """
    Queries DB for a connection with the current radio
    equal to the specified radio_id that has more than 0 remaining updates
    @return: the connections as an untupled list of rows
    """
    stmt = (select(Connections).where(Connections.search_remaining_update > 0))
    return session.all(stmt)


def get_preferred_radios(session, connection_id):
    """
    Queries DB for preferred Radios from a connection
    :param connection_id: specified connection
    :return: list of all preferred radios
    """
    stmt = select(ConnectionPreferredRadios).where(ConnectionPreferredRadios.connection_id == connection_id)
    return session.all(stmt)


def get_connections_id_by_radio(session, radio_id):
    """
    Queries DB for a connection where the current radio equals the parameter radio_id and the state is allowed
    @param radio_id: the primary key to be searched for
    @return: the connection as a list of rows
    """
    stmt = (select(ConnectionPreferredRadios.connection_id).where(ConnectionPreferredRadios.radio_id == radio_id))
    return session.all(stmt)


def switch_to_working_radio(session, connection_id):
    """
    Selects a radio for the connection that fits all filtered requirements
    @param connection_id: the specified connection that should switch the radio
    @return: the radio_id of the new radio, or None
    """
    connection = get_connection(session, connection_id)
    allowed_states = helper_get_allowed_states(connection)

    stmt = (select(Radios).join(ConnectionPreferredRadios, Radios.id == ConnectionPreferredRadios.radio_id)
            .where(ConnectionPreferredRadios.connection_id == connection_id)
            .where(Radios.status_id.in_(allowed_states)).order_by(ConnectionPreferredRadios.priority.asc()))

    radio = session.first(stmt)

    if radio is None:
        # TODO: add genre fallback
        pass

    if radio is None:
        # select 'random' radio
        # TODO: give user status about that it doesn't not a preferred radio
        # TODO: with random
        stmt = (select(Radios)
                .where(Radios.status_id.in_(allowed_states)))
        radio = session.first(stmt)

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


def get_preferred_genres(session, connection_id):
    """
    Queries DB for preferred Genres from a connection
    :param connection_id: specified connection
    :return: list of all preferred genres
    """
    stmt = select(ConnectionPreferredGenres).where(ConnectionPreferredGenres.connection_id == connection_id)
    return session.all(stmt)


def get_connection_favorites(session, connection_id):
    """
    Queries DB for search favorites from a Connection
    :param connection_id: specified connection
    :return: list of all search favorites
    """
    stmt = select(ConnectionSearchFavorites).where(ConnectionSearchFavorites.connection_id == connection_id)
    return session.all(stmt)


def get_connection(session, connection_id):
    """
    Queries DB for specified connection
    :param connection_id: specifies connection
    :return: list of all connection attributes
    """
    stmt = select(Connections).where(Connections.id == connection_id)
    return session.first(stmt)


def insert_new_connection(session, search_query=None, current_radio_id=None, search_without_ads=None,
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
    return session.scalar(stmt)


def insert_into_connection_preferred_radios(session, radio_ids, connection_id):
    """
    Inserts the radio_ids and connection id in the connection_preferred_radios table,
    make sure to delete old values for connection before calling this again with same connection!!!
    @param radio_ids: array with preferred radios
    @param connection_id: the corresponding connection id
    @return: -
    """

    # TODO turn into one single statement
    for radio_id in radio_ids:
        session.execute(insert(ConnectionPreferredRadios), [{"radio_id": radio_id, "connection_id": connection_id}])


def insert_into_connection_search_favorites(session, radio_ids, connection_id):
    """
    Inserts the radio_ids and connection id in the connection_search_favorites table,
    make sure to delete old values for connection before calling this again with same connection!!!
    @param radio_ids: array with preferred radios
    @param connection_id: the corresponding connection id
    @return: -
    """

    # TODO turn into one single statement
    for radio_id in radio_ids:
        session.execute(insert(ConnectionSearchFavorites), [{"radio_id": radio_id, "connection_id": connection_id}])


def insert_into_connection_preferred_genres(session, genre_ids, connection_id):
    """
    Inserts the genre_ids and connection id in the connection_preferred_genres table,
    make sure to delete old values for connection before calling this again with same connection!!!
    @param genre_ids: array with preferred genres
    @param connection_id: the corresponding connection id
    @return: -
    """

    # TODO turn into one single statement
    for genre_id in genre_ids:
        session.execute(insert(ConnectionPreferredGenres), [{"genre_id": genre_id, "connection_id": connection_id}])


def delete_connection_from_db(session, connection_id):
    """
    Removes all entries from "connections", "connection_search_favorites", "connection_preferred_radios",
    "connection_preferred_genres", entries with specified connection_od
    @param connection_id: the connection to be delete
    @return -

    """

    stmt = delete(Connections).where(Connections.id == connection_id)
    session.execute(stmt)


def delete_all_connections_from_db(session):
    """
    Deletes all connections from the DB, used on Serverstart/crash
    @return: -
    """
    session.execute(text("""TRUNCATE TABLE connections CASCADE"""))


def update_search_remaining_updates(session, connection_id, value=None):
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


def update_search_request_for_connection(session, connection_id, search_query=None, without_ads=False, ids=None,
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


def update_preferences_for_connection(session, connection_id, preferred_radios=None, preferred_genres=None, preference_ad=None,
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
        prio = 1
        for i in preferred_radios:
            stmt = insert(ConnectionPreferredRadios).values(connection_id=connection_id, radio_id=i, priority=prio)
            session.execute(stmt)
            prio += 1

    stmt = delete(ConnectionPreferredGenres).where(ConnectionPreferredGenres.connection_id == connection_id)
    session.execute(stmt)

    if isinstance(preferred_genres, list) and len(preferred_genres) > 0:
        stmt = insert(ConnectionPreferredGenres)
        session.execute(stmt, [
            {"connection_id": connection_id, "genre_id": i}
            for i in preferred_genres
        ])


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


def get_radios_that_need_switch_by_time_and_update(session, now_min):
    """
    Querys the DB for the radios that need to be switched away from
    @return: the list of rows of radios
    #"""
    now = func.current_timestamp()
    # if inDerZeitVonWerbung xor status == 'werbung'

    hour_check = func.date_part('hour', now).between(RadioAdTime.ad_transmission_start, RadioAdTime.ad_transmission_end)
    minute_check = func.date_part('minute', now).between(RadioAdTime.ad_start_time, RadioAdTime.ad_end_time - 1)

    ad_check = and_(hour_check, minute_check)
    current_status_is_ad = Radios.status_id == STATUS['ad']

    stmt = (select(Radios).join(RadioAdTime, RadioAdTime.radio_id == Radios.id)
    .where(xor_(
        ad_check,
        current_status_is_ad)
    ))

    select_ids = select(Radios.id).join(RadioAdTime, RadioAdTime.radio_id == Radios.id)
    select_ads = select_ids.where(ad_check)
    select_not_ads = select_ids.where(not_(ad_check))
    switch_radios = session.all(stmt)

    stmt2 = update(Radios).where(Radios.id.in_(select_ads)).values(status_id=STATUS['ad'])
    stmt3 = update(Radios).where(Radios.id.in_(select_not_ads)).values(status_id=STATUS['music'])
    session.execute(stmt2)
    session.execute(stmt3)

    stmt4a = (select(func.min(RadioAdTime.ad_start_time))
              .where(RadioAdTime.ad_start_time > now_min))

    next_start_min = session.all(stmt4a)

    stmt4b = (select(func.min(RadioAdTime.ad_end_time))
              .where(RadioAdTime.ad_end_time > now_min))

    next_end_min = session.all(stmt4b)
    if next_end_min[0] is not None and next_start_min[0] is not None:
        next_event = min(next_end_min[0], next_start_min[0])
    elif next_end_min[0] is not None:
        next_event = next_end_min[0]
    elif next_start_min[0] is not None:
        next_event = next_start_min[0]
    else:
        stmt5a = (select(func.min(RadioAdTime.ad_start_time))
                  .where(RadioAdTime.ad_start_time <= now_min))

        next_start_min = session.all(stmt5a)

        stmt5b = (select(func.min(RadioAdTime.ad_end_time))
                  .where(RadioAdTime.ad_end_time <= now_min))

        next_end_min = session.all(stmt5b)
        if next_end_min[0] is not None and next_start_min[0] is not None:
            next_event = min(next_end_min[0], next_start_min[0])

        elif next_end_min[0] is not None:
            next_event = next_end_min[0]

        elif next_start_min[0] is not None:
            next_event = next_start_min[0]
        else:
            next_event = None
    return [switch_radios, next_event]


def get_radios_and_update_by_currently_playing(session, data):
    radios = []
    for item in data:
        title, station_id = item['title'], item['stationId']
        currently_playing = title.split(': ')

        if len(currently_playing) == 1:
            currently_playing = title.split(' - ')

        if len(currently_playing) == 1:
            currently_playing.append(None)

        stmt = (select(Radios)
                .where(Radios.currently_playing != currently_playing[1])
                .where(Radios.current_interpret != currently_playing[0])
                .where(Radios.station_id == station_id))
        result = session.first(stmt)

        if result is not None:
            radios.append(result)

        latest_played_song = session.first((select(RadioMetadata)
                                   .where(RadioMetadata.station_id == station_id)
                                   .order_by(RadioMetadata.id.desc())))

        if (latest_played_song is None or
                latest_played_song.title != currently_playing[1] and
                latest_played_song.interpret != currently_playing[0]):
            stmt2 = (insert(RadioMetadata).values(station_id=station_id,
                                                  title=currently_playing[1],
                                                  interpret=currently_playing[0],
                                                  timestamp=datetime.now()))
            session.execute(stmt2)

        stmt3 = update(Radios).where(Radios.station_id == station_id).values(
            current_interpret=currently_playing[0],
            currently_playing=currently_playing[1])
        session.execute(stmt3)

    return radios
