from datetime import datetime

import sqlalchemy.sql
from sqlalchemy import *
from api.db.db_helpers import STATUS, helper_get_allowed_states, current_session
from api.db.models import Radios, Connections, ConnectionSearchFavorites, ConnectionPreferredRadios, \
    RadioAdTime, RadioMetadata, RadioStates


# to access list elements, first loop through the rows, then access the db attribute, will return empty list if no
# query result
def get_radio_by_id(radio_id):
    """
    Queries DB for radio by specified id
    :param session: the session to use
    :param radio_id: the radio_id to be filtered by
    :return: the Query result as a row
    """

    session = current_session.get()
    stmt = select(Radios).where(Radios.id == radio_id)
    return session.first(stmt)


def get_radio_by_connection(connection_id):
    """
    Matches the preferred Radios to the specified connection
    @param connection_id: 
    @return: a joined table of the radios and connections
    """
    session = current_session.get()
    stmt = (select(Radios, Connections)
            .join(ConnectionPreferredRadios, Radios.id == ConnectionPreferredRadios.radio_id)
            .join(Connections, ConnectionPreferredRadios.connection_id == connection_id))
    return session.first(stmt)


def get_all_radios():
    """
    Queries DB for all radios
    @return: list of rows with radio entries (empty list if none found)
    """

    session = current_session.get()
    stmt = select(Radios)
    return session.all(stmt)


def radios_existing(radio_ids):
    """
    Checks given list of ids for their existance in the db
    @param radio_ids list of radio ids
    @return: true if every id exists
    """

    session = current_session.get()
    stmt = select(func.count()).select_from(Radios).where(Radios.id.in_(radio_ids))
    count = session.scalar(stmt)
    return count == len(radio_ids)


def get_radio_by_query(search_query=None, search_without_ads=None, ids=None):
    """
    Queries DB for radioname from query
    @param search_query: the query string to search a radio by. Leave blank to search all
    @param search_without_ads: defines whether radio with ads should be returned
    @param ids: the favorites to filter for. Leave blank to search all
    @return: list of rows with radio entries (empty list if none found)
    """

    session = current_session.get()

    stmt = select(Radios)

    if search_query:
        stmt = stmt.where(Radios.name.like("%" + search_query + "%"))

    if search_without_ads:
        stmt = stmt.where(Radios.status_id != STATUS["ad"])

    if ids:
        stmt = stmt.where(Radios.id.in_(ids))

    return session.all(stmt)


def get_connections_by_remaining_updates():
    """
    Queries DB for a connection with the current radio
    equal to the specified radio_id that has more than 0 remaining updates
    @return: the connections as an untupled list of rows
    """

    session = current_session.get()
    stmt = (select(Connections).where(Connections.search_remaining_update > 0))
    return session.all(stmt)


def get_preferred_radios(connection_id):
    """
    Queries DB for preferred Radios from a connection
    :param connection_id: specified connection
    :return: list of all preferred radios
    """

    session = current_session.get()
    stmt = select(ConnectionPreferredRadios).where(ConnectionPreferredRadios.connection_id == connection_id)
    return session.all(stmt)


def get_connections_id_by_radio(radio_id):
    """
    Queries DB for a connection where the current radio equals the parameter radio_id and the state is allowed
    @param radio_id: the primary key to be searched for
    @return: the connection as a list of rows
    """

    session = current_session.get()
    stmt = (select(ConnectionPreferredRadios.connection_id).where(ConnectionPreferredRadios.radio_id == radio_id))
    return session.all(stmt)


def switch_to_working_radio(connection_id):
    """
    Selects a radio for the connection that fits all filtered requirements
    @param connection_id: the specified connection that should switch the radio
    @return: the radio_id of the new radio, or None
    """

    session = current_session.get()

    connection = get_connection(connection_id)
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


def get_connection_favorites(connection_id):
    """
    Queries DB for search favorites from a Connection
    :param connection_id: specified connection
    :return: list of all search favorites
    """

    session = current_session.get()
    stmt = select(ConnectionSearchFavorites).where(ConnectionSearchFavorites.connection_id == connection_id)
    return session.all(stmt)


def get_connection(connection_id):
    """
    Queries DB for specified connection
    :param connection_id: specifies connection
    :return: list of all connection attributes
    """

    session = current_session.get()
    stmt = select(Connections).where(Connections.id == connection_id)
    return session.first(stmt)


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

    session = current_session.get()

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


def insert_into_connection_preferred_radios(radio_ids, connection_id):
    """
    Inserts the radio_ids and connection id in the connection_preferred_radios table,
    make sure to delete old values for connection before calling this again with same connection!!!
    @param radio_ids: array with preferred radios
    @param connection_id: the corresponding connection id
    @return: -
    """

    session = current_session.get()

    # TODO turn into one single statement
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

    session = current_session.get()

    # TODO turn into one single statement
    for radio_id in radio_ids:
        session.execute(insert(ConnectionSearchFavorites), [{"radio_id": radio_id, "connection_id": connection_id}])


def delete_connection_from_db(connection_id):
    """
    Removes all entries from "connections", "connection_search_favorites", "connection_preferred_radios",
    "connection_preferred_genres", entries with specified connection_od
    @param connection_id: the connection to be delete
    @return -

    """

    session = current_session.get()

    stmt = delete(Connections).where(Connections.id == connection_id)
    session.execute(stmt)


def delete_all_connections_from_db():
    """
    Deletes all connections from the DB, used on Serverstart/crash
    @return: -
    """

    session = current_session.get()
    session.execute(text("""TRUNCATE TABLE connections CASCADE"""))


def update_search_remaining_updates(connection_id, value=None):
    """
    Updates the DB attribute search_remaining_update
    @param connection_id: the corresponding connection_id
    @param value: amount of updates that should be remaining. If left blank, it decrements by one
    @return: the amount of remaining updates or 0
    """

    session = current_session.get()

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

    session = current_session.get()

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

    session = current_session.get()

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


def get_radios_that_need_switch_by_time_and_update(now_min):
    """
    Querys the DB for the radios that need to be switched away from
    @return: the list of rows of radios
    #"""

    session = current_session.get()

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


def get_radios_and_update_by_currently_playing(data):
    session = current_session.get()

    radios = []
    for item in data:
        title, station_id = item['title'], item['stationId']
        currently_playing = title.split(': ')

        if len(currently_playing) == 1:
            currently_playing = title.split(' - ')

        if len(currently_playing) == 1:
            currently_playing.append('')

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


def insert_init():
    session = current_session.get()
    radiostatesstmt = (insert(RadioStates).values(id=1, label='Werbung'))
    session.execute(radiostatesstmt)
    radiostatesstmt = (insert(RadioStates).values(id=2, label='Musik'))
    session.execute(radiostatesstmt)
    radiostatesstmt = (insert(RadioStates).values(id=3, label='Nachrichten'))
    session.execute(radiostatesstmt)
    radiostatesstmt = (insert(RadioStates).values(id=4, label=None))
    session.execute(radiostatesstmt)

    radiostmt = (insert(Radios).values
                 (id=1,
                  name='1Live',
                  status_id=2,
                  currently_playing=None,
                  current_interpret=None,
                  stream_url='https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3?aggregator=radio-de',
                  logo_url='https://www.radio.de/images/broadcasts/4e/0d/1382/4/c100.png',
                  station_id='1live')
                 )
    session.execute(radiostmt)
    radiostmt = (insert(Radios).values
                 (id=2,
                  name='WDR 2',
                  status_id=2,
                  currently_playing=None,
                  current_interpret=None,
                  stream_url='https://d121.rndfnk.com/ard/wdr/wdr2/rheinland/mp3/128/stream.mp3?cid=01FBS03TJ7KW307WSY5W0W4NYB&sid=2WfgdbO7GvnQL9AwD8vhvPZ9fs0&token=cz5XFBkPm158lD9VGL4JxM-2zzMfE_3qEd-sX_kdaAA&tvf=x6sCXJp9jRdkMTIxLnJuZGZuay5jb20',
                  logo_url='https://www.radio.de/images/broadcasts/96/67/2279/1/c100.png',
                  station_id='wdr2')
                 )
    session.execute(radiostmt)
    radiostmt = (insert(Radios).values
                 (id=3,
                  name='100,5',
                  status_id=2,
                  currently_playing=None,
                  current_interpret=None,
                  stream_url='https://stream.dashitradio.de/dashitradio/mp3-128/stream.mp3?ref',
                  logo_url='https://www.radio.de/images/broadcasts/90/0e/9857/3/c100.png',
                  station_id='dashitradio')
                 )
    session.execute(radiostmt)
    radiostmt = (insert(Radios).values
                 (id=4,
                  name='Antenne AC',
                  status_id=2,
                  currently_playing=None,
                  current_interpret=None,
                  stream_url='https://antenneac--di--nacs-ais-lgc--06--cdn.cast.addradio.de/antenneac/live/mp3/high',
                  logo_url='https://www.radio.de/images/broadcasts/9a/a4/1421/1/c100.png',
                  station_id='antenneac')
                 )
    session.execute(radiostmt)
    radiostmt = (insert(Radios).values
                 (id=5,
                  name='bigFM',
                  status_id=2,
                  currently_playing=None,
                  current_interpret=None,
                  stream_url='https://streams.bigfm.de/bigfm-sb-128-mp3',
                  logo_url='https://www.radio.de/images/broadcasts/af/e4/1444/4/c100.png',
                  station_id='bigfm')
                 )
    session.execute(radiostmt)
    radiostmt = (insert(Radios).values
                 (id=6,
                  name='BAYERN 1',
                  status_id=2,
                  currently_playing=None,
                  current_interpret=None,
                  stream_url='https://d121.rndfnk.com/ard/br/br1/franken/mp3/128/stream.mp3?cid=01FCDXH5496KNWQ5HK18GG4HED&sid=2ZDBcNAOweP69799K4rCsFc3Jgw&token=AaURPm1j9atmzP6x_QnojyKUrDLXmpuME5vqVWX1ZI0&tvf=XJJyGEmbnhdkMTIxLnJuZGZuay5jb20',
                  logo_url='https://www.radio.de/images/broadcasts/10/90/2245/2/c100.png',
                  station_id='bayern1main')
                 )
    session.execute(radiostmt)

    radioadtimestmt = (
        insert(RadioAdTime).values(radio_id=1, ad_start_time=53, ad_end_time=3, ad_transmission_start=6,
                                   ad_transmission_end=20))
    session.execute(radioadtimestmt)
    radioadtimestmt = (
        insert(RadioAdTime).values(radio_id=2, ad_start_time=27, ad_end_time=33, ad_transmission_start=6,
                                   ad_transmission_end=20))
    session.execute(radioadtimestmt)
    radioadtimestmt = (
        insert(RadioAdTime).values(radio_id=2, ad_start_time=53, ad_end_time=3, ad_transmission_start=6,
                                   ad_transmission_end=20))
    session.execute(radioadtimestmt)
    radioadtimestmt = (
        insert(RadioAdTime).values(radio_id=6, ad_start_time=27, ad_end_time=33, ad_transmission_start=6,
                                   ad_transmission_end=20))
    session.execute(radioadtimestmt)
    radioadtimestmt = (
        insert(RadioAdTime).values(radio_id=6, ad_start_time=53, ad_end_time=3, ad_transmission_start=6,
                                   ad_transmission_end=20))
    session.execute(radioadtimestmt)

    # aus irgendeinem grund klappen bulk inserts nicht wie in der doku
    # https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html#orm-queryguide-bulk-insert


'''
    radiostatesstmt = (insert(RadioStates),
                   [
                       {"id": 1, "label": 'Werbung'},
                       {"id": 2, "label": 'Musik'},
                       {"id": 3, "label": 'Nachrichten'},
                       {"id": 4, "label": None},
                   ],
                   )
    session.execute(radiostatesstmt)

    # not actively used in current implementation
    genresstmt = (insert(Genres),
              [
                  {"id": 1, "name": 'Pop'},
                  {"id": 2, "name": '90er'},
                  {"id": 3, "name": 'Charts'},
                  {"id": 4, "name": 'Hip Hop'},
                  {"id": 5, "name": 'Oldies'},
                  {"id": 6, "name": '80er'},
              ],
              )
    session.execute(genresstmt)

    radiosstmt = (insert(Radios),
              [
                  {
                      "id": 1,
                      "name": '1Live',
                      "status_id": 2,
                      "currently_playing": None,
                      "current_interpret": None,
                      "stream_url": 'https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3?aggregator=radio-de',
                      "logo_url": 'https://www.radio.de/images/broadcasts/4e/0d/1382/4/c100.png',
                      "station_id": '1live'
                  },
                  {
                      "id": 2,
                      "name": 'WDR 2',
                      "status_id": 2,
                      "currently_playing": None,
                      "current_interpret": None,
                      "stream_url": 'https://d121.rndfnk.com/ard/wdr/wdr2/rheinland/mp3/128/stream.mp3?cid=01FBS03TJ7KW307WSY5W0W4NYB&sid=2WfgdbO7GvnQL9AwD8vhvPZ9fs0&token=cz5XFBkPm158lD9VGL4JxM-2zzMfE_3qEd-sX_kdaAA&tvf=x6sCXJp9jRdkMTIxLnJuZGZuay5jb20',
                      "logo_url": 'https://www.radio.de/images/broadcasts/96/67/2279/1/c100.png',
                      "station_id": 'wdr2'
                  },
                  {
                      "id": 3,
                      "name": '100,5',
                      "status_id": 2,
                      "currently_playing": None,
                      "current_interpret": None,
                      "stream_url": 'https://stream.dashitradio.de/dashitradio/mp3-128/stream.mp3?ref',
                      "logo_url": 'https://www.radio.de/images/broadcasts/90/0e/9857/3/c100.png',
                      "station_id": 'dashitradio'
                  },
                  {
                      "id": 4,
                      "name": 'Antenne AC',
                      "status_id": 2,
                      "currently_playing": None,
                      "current_interpret": None,
                      "stream_url": 'https://antenneac--di--nacs-ais-lgc--06--cdn.cast.addradio.de/antenneac/live/mp3/high',
                      "logo_url": 'https://www.radio.de/images/broadcasts/9a/a4/1421/1/c100.png',
                      "station_id": 'antenneac'
                  },
                  {
                      "id": 5,
                      "name": 'bigFM',
                      "status_id": 2,
                      "currently_playing": None,
                      "current_interpret": None,
                      "stream_url": 'https://streams.bigfm.de/bigfm-sb-128-mp3',
                      "logo_url": 'https://www.radio.de/images/broadcasts/af/e4/1444/4/c100.png',
                      "station_id": 'bigfm'
                  },
                  {
                      "id": 6,
                      "name": 'BAYERN 1',
                      "status_id": 2,
                      "currently_playing": None,
                      "current_interpret": None,
                      "stream_url": 'https://d121.rndfnk.com/ard/br/br1/franken/mp3/128/stream.mp3?cid=01FCDXH5496KNWQ5HK18GG4HED&sid=2ZDBcNAOweP69799K4rCsFc3Jgw&token=AaURPm1j9atmzP6x_QnojyKUrDLXmpuME5vqVWX1ZI0&tvf=XJJyGEmbnhdkMTIxLnJuZGZuay5jb20',
                      "logo_url": 'https://www.radio.de/images/broadcasts/10/90/2245/2/c100.png',
                      "station_id": 'bayern1main'
                  },

              ],
              )
    session.execute(radiosstmt)

    # not actively used in current implementation
    radiogenresstmt = (insert(RadioGenres),
                   [
                       {"radio_id": 1, "genre_id": 1},
                       {"radio_id": 2, "genre_id": 1},
                       {"radio_id": 2, "genre_id": 2},
                       {"radio_id": 3, "genre_id": 1},
                       {"radio_id": 3, "genre_id": 6},
                       {"radio_id": 3, "genre_id": 2},
                       {"radio_id": 4, "genre_id": 1},
                       {"radio_id": 5, "genre_id": 1},
                       {"radio_id": 5, "genre_id": 3},
                       {"radio_id": 5, "genre_id": 4},
                       {"radio_id": 6, "genre_id": 1},
                       {"radio_id": 6, "genre_id": 5},
                   ],
                   )
    session.execute(radiogenresstmt)

    radioadtimestmt = (insert(RadioAdTime),
                   [
                       {"radio_id": 1, "ad_start_time": 53, "ad_end_time": 3, "ad_transmission_start": 6,
                        "ad_transmission_end": 20},
                       {"radio_id": 2, "ad_start_time": 27, "ad_end_time": 33, "ad_transmission_start": 6,
                        "ad_transmission_end": 20},
                       {"radio_id": 2, "ad_start_time": 53, "ad_end_time": 3, "ad_transmission_start": 6,
                        "ad_transmission_end": 20},
                       {"radio_id": 6, "ad_start_time": 27, "ad_end_time": 33, "ad_transmission_start": 6,
                        "ad_transmission_end": 20},
                       {"radio_id": 6, "ad_start_time": 53, "ad_end_time": 3, "ad_transmission_start": 6,
                        "ad_transmission_end": 20},

                   ],
                   )
    session.execute(radioadtimestmt)
'''
