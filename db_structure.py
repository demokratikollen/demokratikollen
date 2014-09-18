# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Member(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    castvotes = relationship("CastVote", backref="member")


class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    castvotes = relationship("CastVote", backref="vote")


class CastVote(Base):
    __tablename__ = "cast_votes"
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    vote_id = Column(Integer, ForeignKey('votes.id'))
    value = Column(String)



if __name__ == '__main__':
    engine = create_engine('sqlite:///test_metadata.db')

    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)

    s = session()
    apa = Member(name="Arne Apa")
    bepa = Vote(name="Bepavotering")
    bepa_yes = CastVote(value="Jo",member=apa,vote=bepa)

    s.add(apa)
    s.add(bepa)
    s.add(bepa_yes)

    s.commit()