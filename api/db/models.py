from dataclasses import dataclass
from datetime import datetime
from sqlalchemy import Integer, ForeignKey, Text, Boolean, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
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
    station_id: Mapped[str] = mapped_column(Text)
    ad_duration: Mapped[int] = mapped_column(Integer)
    ad_until: Mapped[Optional[int]] = mapped_column(Integer)


@dataclass
class RadioStates(Base):
    __tablename__ = 'radio_states'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    label: Mapped[Optional[str]] = mapped_column(Text)


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
class ConnectionSearchFavorites(Base):
    __tablename__ = 'connection_search_favorites'

    radio_id: Mapped[int] = mapped_column(ForeignKey('radios.id'), primary_key=True)
    connection_id: Mapped[int] = mapped_column(ForeignKey('connections.id', ondelete="CASCADE"), primary_key=True)


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


@dataclass
class ConnectionPreferredRadios(Base):
    __tablename__ = 'connection_preferred_radios'

    radio_id: Mapped[int] = mapped_column(ForeignKey('radios.id'), primary_key=True)
    connection_id: Mapped[int] = mapped_column(ForeignKey('connections.id', ondelete="CASCADE"), primary_key=True)
    priority: Mapped[int] = mapped_column(Integer)


@dataclass
class RadioMetadata(Base):
    __tablename__ = 'radio_metadata'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    station_id: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text, nullable=True)
    interpret: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP)
