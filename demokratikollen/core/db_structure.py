# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from sqlalchemy.types import Date, Enum
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
from demokratikollen.core.utils import misc as misc_utils, postgres as pg_utils


Base = declarative_base()

class Member(Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(250))
    last_name = Column(String(250))
    birth_year = Column(Integer)
    gender = Column(String(10))
    image_url = Column(String(250))
    party_id = Column(Integer, ForeignKey('parties.id'))
    votes = relationship('Vote', backref='member')
    appointments = relationship('Appointment', backref='member')

    def __repr__(self):
        return '{}, {} ({})'.format(self.last_name,self.first_name,self.party.abbr)


class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    start_date = Column(Date)
    end_date = Column(Date)
    classtype = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity':'appointment',
        'polymorphic_on':classtype
    }

class GroupAppointment(Appointment):
    __tablename__ = 'group_appointments'
    id = Column(Integer, ForeignKey('appointments.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'))

    __mapper_args__ = {
        'polymorphic_identity':'group_appointment'
    }

class ChamberAppointment(Appointment):
    __tablename__ = 'chamber_appointments'
    id = Column(Integer, ForeignKey('appointments.id'), primary_key=True)
    status = Column(Enum('Ledig','Tjänstgörande',name='chamber_appointment_statuses'))
    role = Column(Enum('Riksdagsledamot','Ersättare',name='chamber_appointment_roles'))
    chair = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity':'chamber_appointment'
    }

    def title(self):
        return '{} {} {}'.format(self.status,self.role,self.member)    
    def __repr__(self):
        return 'Chair {}: {} {} {}-{}: {}'.format(self.chair,self.status,self.role,self.start_date,self.end_date,self.member)    


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    abbr = Column(String(100))
    appointments = relationship('GroupAppointment', backref='group')
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
    def __repr__(self):
        return 'Party {}: {} ({})'.format(self.id,self.name,self.abbr)    


class Poll(Base):
    __tablename__ = 'polls'
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    date = Column(Date)
    votes = relationship('Vote', backref='poll')

    def __repr__(self):
        return self.name



VoteOptionsType = Enum('Ja','Nej','Avstår','Frånvarande',name='vote_options')

class Vote(Base):
    __tablename__ = 'votes'
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    poll_id = Column(Integer, ForeignKey('polls.id'))
    vote_option = Column(VoteOptionsType)

    def __repr__(self):
        return '{}: {}'.format(self.member.__repr__(),self.vote_option.__repr__())



class PartyVote(Base):
    __tablename__ = 'party_votes'
    id = Column(Integer, primary_key=True)
    party_id = Column(Integer, ForeignKey('parties.id'))
    poll_id = Column(Integer, ForeignKey('polls.id'))
    num_yes = Column(Integer)
    num_no = Column(Integer)
    num_abstain = Column(Integer)
    num_absent = Column(Integer)

    def __repr__(self):
        return '{}: {}'.format(self.member.__repr__(),self.vote_option.__repr__())


def create_db_structure(engine):
    if misc_utils.yes_or_no("Do you really want to drop everything in the database?"):
        pg_utils.drop_everything(engine)

    Base.metadata.create_all(engine)


if __name__ == '__main__':
    pass