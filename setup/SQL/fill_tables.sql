-- Fill "radio_states" table

INSERT INTO radio_states(id, label)
VALUES(1, 'Werbung');

INSERT INTO radio_states(id, label)
VALUES(2, 'Musik');

INSERT INTO radio_states(id, label)
VALUES(3, 'Nachrichten');

INSERT INTO radio_states(id, label)
VALUES(4, NULL );


-- Fill "genres" table

INSERT INTO genres(id, name)
VALUES(1, 'Pop');

INSERT INTO genres(id, name)
VALUES(2, '90er');

INSERT INTO genres(id, name)
VALUES(3, 'Charts');

INSERT INTO genres(id, name)
VALUES(4, 'Hip Hop');

INSERT INTO genres(id, name)
VALUES(5, 'Oldies');

INSERT INTO genres(id, name)
VALUES(6, '80er');

-- Fill "radios" table

INSERT INTO radios(id, name, status_id, currently_playing, current_interpret, stream_url, logo_url, station_id)
VALUES(1, '1Live', 2, NULL, NULL,'https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3?aggregator=radio-de' ,'https://www.radio.de/images/broadcasts/4e/0d/1382/4/c100.png', '1live');


INSERT INTO radios(id, name, status_id, currently_playing, current_interpret, stream_url, logo_url, station_id)
VALUES(2, 'WDR 2', 2, NULL, NULL,'https://d121.rndfnk.com/ard/wdr/wdr2/rheinland/mp3/128/stream.mp3?cid=01FBS03TJ7KW307WSY5W0W4NYB&sid=2WfgdbO7GvnQL9AwD8vhvPZ9fs0&token=cz5XFBkPm158lD9VGL4JxM-2zzMfE_3qEd-sX_kdaAA&tvf=x6sCXJp9jRdkMTIxLnJuZGZuay5jb20' ,'https://www.radio.de/images/broadcasts/96/67/2279/1/c100.png', 'wdr2');


INSERT INTO radios(id, name, status_id, currently_playing, current_interpret, stream_url, logo_url, station_id)
VALUES(3, '100,5', 2, NULL, NULL,'https://stream.dashitradio.de/dashitradio/mp3-128/stream.mp3?ref' ,'https://www.radio.de/images/broadcasts/90/0e/9857/3/c100.png', 'dashitradio');


INSERT INTO radios(id, name, status_id, currently_playing, current_interpret, stream_url, logo_url, station_id)
VALUES(4, 'Antenne AC', 2, NULL, NULL,'https://antenneac--di--nacs-ais-lgc--06--cdn.cast.addradio.de/antenneac/live/mp3/high' ,'https://www.radio.de/images/broadcasts/9a/a4/1421/1/c100.png', 'antenneac');


INSERT INTO radios(id, name, status_id, currently_playing, current_interpret, stream_url, logo_url, station_id)
VALUES(5, 'bigFM', 2, NULL, NULL,'https://streams.bigfm.de/bigfm-sb-128-mp3' ,'https://www.radio.de/images/broadcasts/af/e4/1444/4/c100.png', 'bigfm');

INSERT INTO radios(id, name, status_id, currently_playing, current_interpret, stream_url, logo_url, station_id)
VALUES(6, 'BAYERN 1', 2, NULL, NULL,'https://d121.rndfnk.com/ard/br/br1/franken/mp3/128/stream.mp3?cid=01FCDXH5496KNWQ5HK18GG4HED&sid=2ZQzsaDx31ycwBA2nMB7MlYV2YA&token=IFb6h2TZYxGoc5GpDbpQdN00rBQlA4udJfaxFvqbxdI&tvf=WEFQioAboBdkMTIxLnJuZGZuay5jb20' ,'https://www.radio.de/images/broadcasts/10/90/2245/2/c100.png', 'bayern1main');

-- Fill "radio_genres" table

INSERT INTO radio_genres(radio_id, genre_id)
VALUES(1, 1);

INSERT INTO radio_genres(radio_id, genre_id)
VALUES(2, 1);

INSERT INTO radio_genres(radio_id, genre_id)
VALUES(2, 2);

INSERT INTO radio_genres(radio_id, genre_id)
VALUES(3, 1);

INSERT INTO radio_genres(radio_id, genre_id)
VALUES(3, 6);

INSERT INTO radio_genres(radio_id, genre_id)
VALUES(3, 2);

INSERT INTO radio_genres(radio_id, genre_id)
VALUES(4, 1);

INSERT INTO radio_genres(radio_id, genre_id)
VALUES(5, 1);

INSERT INTO radio_genres(radio_id, genre_id)
VALUES(5, 3);

INSERT INTO radio_genres(radio_id, genre_id)
VALUES(5, 4);

INSERT INTO radio_genres(radio_id, genre_id)
VALUES(6, 1);

INSERT INTO radio_genres(radio_id, genre_id)
VALUES(6, 5);
