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

    def __repr__(self):
        return self.name


class Vote(Base):
    __tablename__ = 'votes'
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    poll_id = Column(Integer, ForeignKey('polls.id'))
    vote_option_id = Column(Integer, ForeignKey('vote_options.id'))
    vote_option = relationship("VoteOption",uselist=False)

    def __repr__(self):
        return '{}: {}'.format(self.member.__repr__(),self.vote_option.__repr__())
        




class VoteOption(Base):
    __tablename__ = "vote_options"
    id = Column(Integer, primary_key=True)
    name = Column(String(250))

    def __repr__(self):
        return self.name


def create_db_structure(engine):
    if utils.yes_or_no("Do you really want to drop everything in the database?"):
        utils.drop_everything(engine)
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    engine = create_engine(utils.engine_url())
    create_db_structure(engine)

    session = sessionmaker()
    session.configure(bind=engine)
    s = session()

    vote_yes = VoteOption(name="Ja")
    vote_no = VoteOption(name="Nej")
    vote_abstain = VoteOption(name="Avstår")
    vote_absent = VoteOption(name="Frånvarande")

    s.add(vote_yes)
    s.add(vote_no)
    s.add(vote_abstain)
    s.add(vote_absent)

    party_S = Party(name='Socialdemokraterna',abbr='S')
    party_M = Party(name='Moderata samlingspartiet', abbr='M')
    party_SD = Party(name='Sverigedemokraterna', abbr="SD")
    party_V = Party(name='Vänsterpartiet',abbr='V')

    s.add(party_S)
    s.add(party_M)
    s.add(party_SD)
    s.add(party_V)

    member1 = Member(first_name='Stefan',last_name='Löfvén',party=party_S)
    member2 = Member(first_name='Jimmie',last_name='Åkesson',party=party_SD)
    member3 = Member(first_name='Fredrik', last_name='Reinfeldt', party=party_M)
    member4 = Member(first_name='Jonas', last_name='Sjöstedt', party=party_V)

    s.add(member1)
    s.add(member2)
    s.add(member3)
    s.add(member4)

    poll1 = Poll(name='Ska Stefan få bli statsminister?')
    s.add(poll1)
    s.add(Vote(member=member1,poll=poll1,vote_option=vote_yes))
    s.add(Vote(member=member2,poll=poll1,vote_option=vote_no))
    s.add(Vote(member=member3,poll=poll1,vote_option=vote_abstain))
    s.add(Vote(member=member4,poll=poll1,vote_option=vote_yes))

    poll2 = Poll(name='Ska vi höja barnbidraget?')
    s.add(poll2)
    s.add(Vote(member=member1,poll=poll2,vote_option=vote_yes))
    s.add(Vote(member=member2,poll=poll2,vote_option=vote_no))
    s.add(Vote(member=member3,poll=poll2,vote_option=vote_no))
    s.add(Vote(member=member4,poll=poll2,vote_option=vote_yes))    

    start = datetime.datetime.strptime('2010-01-01', '%Y-%m-%d').date()
    end = datetime.datetime.strptime('2011-12-12', '%Y-%m-%d').date()
    s.add(Appointment(group=party_S,member=member1,start_date=start,end_date=end))

    s.commit()