from dataclasses import dataclass

from sqlalchemy import Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import MetaData
from typing import Optional

metadata_obj = MetaData()


# The following class maps python Objects to PostgreSQL tables

@dataclass
class Base(DeclarativeBase):
    pass


@dataclass
class Radios(Base):
    __tablename__ = 'radios'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    status_id: Mapped[int] = mapped_column(Integer)
    currently_playing: Mapped[Optional[str]] = mapped_column(Text)
    current_interpret: Mapped[Optional[str]] = mapped_column(Text)
    stream_url: Mapped[str] = mapped_column(Text)
    logo_url: Mapped[str] = mapped_column(Text)


@dataclass
class RadioStates(Base):
    __tablename__ = 'radio_states'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    label: Mapped[Optional[str]] = mapped_column(Text)


@dataclass
class RadioGenres(Base):
    __tablename__ = 'radio_genres'

    radio_id: Mapped[int] = mapped_column(ForeignKey("radios.id"), primary_key=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"), primary_key=True)


@dataclass
class RadioAdTime(Base):
    __tablename__ = 'radio_ad_time'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    radio_id: Mapped[int] = mapped_column(ForeignKey("radios.id"))
    ad_start_time: Mapped[int] = mapped_column(Integer)
    ad_end_time: Mapped[int] = mapped_column(Integer)
    ad_transmission_start: Mapped[int] = mapped_column(Integer)
    ad_transmission_end: Mapped[int] = mapped_column(Integer)


@dataclass
class Genres(Base):
    __tablename__ = 'genres'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)


@dataclass
class ConnectionSearchFavorites(Base):
    __tablename__ = 'connection_search_favorites'

    radio_id: Mapped[int] = mapped_column(ForeignKey('radios.id'), primary_key=True)
    connection_id: Mapped[int] = mapped_column(ForeignKey('connections.id', ondelete="CASCADE"), primary_key=True)

    # parent = relationship("Connections", back_populates="childSearchFav")


@dataclass
class Connections(Base):
    __tablename__ = 'connections'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    search_query: Mapped[Optional[str]] = mapped_column(Text)
    current_radio_id: Mapped[Optional[int]] = mapped_column(ForeignKey('radios.id'))
    search_without_ads: Mapped[Optional[bool]] = mapped_column(Boolean)
    search_remaining_update: Mapped[int] = mapped_column(Integer, default=0)
    preference_music: Mapped[Optional[bool]] = mapped_column(Boolean)
    preference_talk: Mapped[Optional[bool]] = mapped_column(Boolean)
    preference_news: Mapped[Optional[bool]] = mapped_column(Boolean)
    preference_ad: Mapped[Optional[bool]] = mapped_column(Boolean)

    # favorites = relationship(Radios, secondary='connection_search_favorites', backref='favorite_for_connections')
    # preferred_radios = relationship(Radios, secondary='connection_preferred_radios', backref='preferred_by_connections')
    # preferred_genres = relationship(Genres, secondary='connection_preferred_genres', backref='preferred_by_connections')
    # current_radio = relationship(Radios, backref='connections_currently_playing')

    # Die 3 Zeilen werfen Warnings, weil es wegen den reltionships hierdrueber, mehrere relationships ueber den
    # gleichen Secondary Key gibt
    # childPrefRadios = relationship("ConnectionPreferredRadios", back_populates="parent", cascade="all, delete",
    #                                 )
    # childPrefGenres = relationship("ConnectionPreferredGenres", back_populates="parent", cascade="all, delete",
    #                                )
    # childSearchFav = relationship("ConnectionSearchFavorites", back_populates="parent", cascade="all, delete",
    #                               )


@dataclass
class ConnectionPreferredRadios(Base):
    __tablename__ = 'connection_preferred_radios'

    radio_id: Mapped[int] = mapped_column(ForeignKey('radios.id'), primary_key=True)
    connection_id: Mapped[int] = mapped_column(ForeignKey('connections.id', ondelete="CASCADE"), primary_key=True)

    # parent = relationship("Connections", back_populates="childPrefRadios")


@dataclass
class ConnectionPreferredGenres(Base):
    __tablename__ = 'connection_preferred_genres'

    genre_id: Mapped[int] = mapped_column(ForeignKey('genres.id'), primary_key=True)
    connection_id: Mapped[int] = mapped_column(ForeignKey('connections.id', ondelete="CASCADE"), primary_key=True)

    # parent = relationship("Connections", back_populates="childPrefGenres")
