# -*- coding: utf-8 -*-
from demokratikollen.core.db_structure import *
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from demokratikollen.core.utils import postgres as pg_utils
import os
import psycopg2 as pg
from progress_bar import InitBar


# Connect to SQLAlchemy db and create structure
engine = create_engine(pg_utils.engine_url())
session = sessionmaker()
session.configure(bind=engine)
s = session()





# Party votes
num_party_votes = 0
num_polls = s.query(func.count(PolledPoint.id)).scalar()
pbar = InitBar(title="Computing party votes")
pbar(0)
n=0
for polled_point in s.query(PolledPoint):
    n = n+1
    if n % 10 == 0:
        pbar(100*n/num_polls)


    votes = s.query(Vote).join(Member).join(Party) \
        .filter(Vote.polled_point_id == polled_point.id) \
        .order_by(Party.id)

    current_party_id = 0
    for vote in votes:
        if current_party_id != vote.member.party_id:
            if not current_party_id == 0:
                s.add(PartyVote(party_id = current_party_id,
                                polled_point_id = polled_point.id,
                                num_yes = party_votes['Ja']                             ,
                                num_no = party_votes['Nej'],
                                num_abstain = party_votes['Avstår'],
                                num_absent = party_votes['Frånvarande']))

            current_party_id = vote.member.party_id
            party_votes = {
                'Ja': 0,
                'Nej': 0,
                'Avstår': 0,
                'Frånvarande': 0
            }

        party_votes[vote.vote_option] += 1

    s.add(PartyVote(party_id = current_party_id,
                    polled_point_id = polled_point.id,
                    num_yes = party_votes['Ja']                             ,
                    num_no = party_votes['Nej'],
                    num_abstain = party_votes['Avstår'],
                    num_absent = party_votes['Frånvarande']))


s.commit()
