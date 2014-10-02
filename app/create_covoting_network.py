# -*- coding: utf-8 -*-
from db_structure import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, aliased
from itertools import combinations

engine = create_engine(utils.engine_url())

session = sessionmaker(bind=engine)
s = session()

for poll in s.query(Poll):
	print poll.__repr__().encode('utf-8')
	for vote in poll.votes:
		print vote.__repr__().encode('utf-8')

vote1 = aliased(Vote)
vote2 = aliased(Vote)

absent_vote = s.query(VoteOption).filter(VoteOption.name=='Frånvarande').one()

for (m1,m2) in combinations(s.query(Member), 2):
	
	antal = s.query(vote1, vote2) \
		.filter(vote1.member_id == m1.id) \
		.filter(vote2.member_id == m2.id) \
		.filter(vote1.vote_option_id == vote2.vote_option_id) \
		.filter(vote1.vote_option_id != absent_vote.id) \
		.filter(vote2.vote_option_id != absent_vote.id) \
		.filter(vote1.poll_id == vote2.poll_id).count()
	print '{} och {}: {}'.format(m1.id,m2.id,antal)
