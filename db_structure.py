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
    votes = relationship('Vote', backref='member')
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


class Poll(Base):
    __tablename__ = 'polls'
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    votes = relationship('Vote', backref='poll')


class Vote(Base):
    __tablename__ = 'votes'
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    poll_id = Column(Integer, ForeignKey('polls.id'))
    vote_option_id = Column(Integer, ForeignKey('vote_options.id'))
    vote_option = relationship("VoteOption")


class VoteOption(Base):
    __tablename__ = "vote_options"
    id = Column(Integer, primary_key=True)
    name = Column(String(250))



if __name__ == '__main__':
    engine = create_engine('postgresql+psycopg2://postgres:demokrati@localhost:5432/demokratikollen')

    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    s = session()
    apa = Member(name='Arne Apa')
    bepa = Poll(name='Bepavotering')
    yes = VoteOption(name="yes")
    bepa_yes = Vote(member=apa,poll=bepa,vote_option=yes)
    kam = Unit(name='kam')
    start = datetime.datetime.strptime('2010-01-01', '%Y-%m-%d').date()
    end = datetime.datetime.strptime('2011-12-12', '%Y-%m-%d').date()
    uppdrag = Assignment(unit=kam,member=apa,start_date=start,end_date=end)


    s.add(apa)
    s.add(bepa)
    s.add(yes)
    s.add(bepa_yes)
    s.add(kam)
    s.add(uppdrag)

    s.commit()