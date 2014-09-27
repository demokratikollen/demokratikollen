# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from sqlalchemy.types import Date
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Member(Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    castvotes = relationship('CastVote', backref='member')
    assignments = relationship('Assignment', backref='member')


class Assignment(Base):
    __tablename__ = 'assignments'
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    unit_id = Column(Integer, ForeignKey('units.id'))
    start_date = Column(Date)
    end_date = Column(Date)


class Unit(Base):
    __tablename__ = 'units'
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    assignments = relationship('Assignment', backref='unit')


class Vote(Base):
    __tablename__ = 'votes'
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    castvotes = relationship('CastVote', backref='vote')


class CastVote(Base):
    __tablename__ = 'cast_votes'
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    vote_id = Column(Integer, ForeignKey('votes.id'))
    value = Column(String)



if __name__ == '__main__':
    engine = create_engine('postgresql+psycopg2://postgres:demokrati@localhost:5432/demokratikollen')

    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)

    s = session()
    apa = Member(name='Arne Apa')
    bepa = Vote(name='Bepavotering')
    bepa_yes = CastVote(value='Jo',member=apa,vote=bepa)
    kam = Unit(name='kam')
    start = datetime.datetime.strptime('2010-01-01', '%Y-%m-%d').date()
    end = datetime.datetime.strptime('2011-12-12', '%Y-%m-%d').date()
    uppdrag = Assignment(unit=kam,member=apa,start_date=start,end_date=end)


    s.add(apa)
    s.add(bepa)
    s.add(bepa_yes)
    s.add(kam)
    s.add(uppdrag)

    s.commit()