# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from sqlalchemy.types import Date
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
import utils


Base = declarative_base()

class Member(Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(250))
    last_name = Column(String(250))
    party_id = Column(Integer, ForeignKey('parties.id'))
    votes = relationship('Vote', backref='member')
    appointments = relationship('Appointment', backref='member')

    def __repr__(self):
        return '{}, {} ({})'.format(self.last_name,self.first_name,self.party.abbr)


class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))
    start_date = Column(Date)
    end_date = Column(Date)


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    abbr = Column(String(100))
    appointments = relationship('Appointment', backref='group')
    classtype = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity':'group',
        'polymorphic_on':classtype
    }


class Party(Group):
    __tablename__ = 'parties'
    id = Column(Integer, ForeignKey('groups.id'), primary_key=True)
    members = relationship('Member', backref='party')

    __mapper_args__ = {
        'polymorphic_identity':'party',
    }


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
    vote_option = relationship("VoteOption",uselist=False)


class VoteOption(Base):
    __tablename__ = "vote_options"
    id = Column(Integer, primary_key=True)
    name = Column(String(250))

def create_db_structure(engine):
    if utils.yes_or_no("Do you really want to drop everything in the database?"):
        utils.drop_everything(engine)
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    engine = create_engine('postgresql+psycopg2://postgres:demokrati@localhost:5432/demokratikollen')
    create_db_structure(engine)

    session = sessionmaker()
    session.configure(bind=engine)
    s = session()

    sossarna = Party(name='Socialdemokraterna',abbr='S')

    apa = Member(first_name='Arne',last_name='Apa',party=sossarna)
    bepa = Poll(name='Bepavotering')
    yes = VoteOption(name="yes")
    bepa_yes = Vote(member=apa,poll=bepa,vote_option=yes)
    start = datetime.datetime.strptime('2010-01-01', '%Y-%m-%d').date()
    end = datetime.datetime.strptime('2011-12-12', '%Y-%m-%d').date()
    uppdrag = Appointment(group=sossarna,member=apa,start_date=start,end_date=end)

    print apa.party.name
    print ','.join(map(str,sossarna.members))

    s.add(sossarna)
    s.add(apa)
    s.add(bepa)
    s.add(yes)
    s.add(bepa_yes)
    s.add(uppdrag)

    s.commit()