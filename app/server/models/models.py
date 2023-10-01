
from sqlalchemy import Boolean, Column, Float, Numeric, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.server.database import Base

class Sport(Base):
    __tablename__ = 'sports'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    slug = Column(String, unique=True)
    is_active = Column(Boolean, default=True)

    events = relationship('Event', back_populates='sport')


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    slug = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    event_type = Column(String)
    sport_id = Column(Integer, ForeignKey('sports.id'))
    status = Column(String)
    scheduled_start = Column(DateTime)
    actual_start = Column(DateTime)

    sport = relationship('Sport', back_populates='events')
    selections = relationship('Selection', back_populates='event')



class Selection(Base):
    __tablename__ = 'selections'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    event_id = Column(Integer, ForeignKey('events.id'))
    price = Column(Numeric)
    is_active = Column(Boolean, default=True)
    outcome = Column(String)

    event = relationship('Event', back_populates='selections')


