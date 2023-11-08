from sqlalchemy import Integer, ForeignKey, Text, TIMESTAMP, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import MetaData
from typing import Optional



import datetime

metadata_obj = MetaData()
class Base(DeclarativeBase):
    type_annotation_map = {
        datetime.datetime: TIMESTAMP(timezone=False)
    }


class Radio(Base):
    __tablename__ = 'radios'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    status_id: Mapped[str] = mapped_column(Text)
    currently_playing: Mapped[Optional[str]] = mapped_column(Text)
    current_interpret: Mapped[Optional[str]] = mapped_column(Text)
    stream_url: Mapped[str] = mapped_column(Text)
    logo_url: Mapped[str] = mapped_column(Text)


class RadioStates(Base):
    __tablename__ = 'radio_states'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    label: Mapped[Optional[str]] = mapped_column(Text)


class RadioGenres(Base):
    __tablename__ = 'radio_genres'

    radio_id: Mapped[int] = mapped_column(ForeignKey("radios.id"), primary_key=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"), primary_key=True)


class RadioAdTime(Base):
    __tablename__ = 'radio_ad_time'

    radio_id: Mapped[int] = mapped_column(ForeignKey("radios.id"), primary_key=True)
    ad_start_time: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, primary_key=True)
    ad_end_time: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, primary_key=True)
    ad_transmission_start: Mapped[datetime.datetime] = mapped_column(TIMESTAMP)
    ad_transmission_end: Mapped[datetime.datetime] = mapped_column(TIMESTAMP)


class Genres(Base):
    __tablename__ = 'genres'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)


class Connections(Base):
    __tablename__ = 'connections'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    search_query: Mapped[str] = mapped_column(Text)
    current_radio_id: Mapped[Optional[int]] = mapped_column(Integer)
    search_without_ads: Mapped[bool] = mapped_column(Boolean)
    search_remaining_update: Mapped[int] = mapped_column(Integer)
    preference_music: Mapped[bool] = mapped_column(Boolean)
    preference_talk: Mapped[bool] = mapped_column(Boolean)
    preference_news: Mapped[bool] = mapped_column(Boolean)
    preference_ad: Mapped[bool] = mapped_column(Boolean)


class ConnectionSearchFavorites(Base):
    __tablename__ = 'connection_search_favorites'

    radio_id: Mapped[int] = mapped_column(ForeignKey('radios.id'), primary_key=True)
    connection_id: Mapped[int] = mapped_column(ForeignKey('connections.id'), primary_key=True)


class ConnectionPreferredRadios(Base):
    __tablename__ = 'connection_preferred_radios'

    radio_id: Mapped[int] = mapped_column(ForeignKey('radios.id'), primary_key=True)
    connection_id: Mapped[int] = mapped_column(ForeignKey('connections.id'), primary_key=True)


class ConnectionPreferredGenres(Base):
    __tablename__ = 'connection_preferred_genres'

    genre_id: Mapped[int] = mapped_column(ForeignKey('genres.id'), primary_key=True)
    connection_id: Mapped[int] = mapped_column(ForeignKey('connections.id'), primary_key=True)
