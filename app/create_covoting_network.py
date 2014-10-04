from db_structure import *
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker, aliased
from itertools import combinations
import utils

engine = create_engine(utils.engine_url())

session = sessionmaker(bind=engine)
s = session()


absent_vote = s.query(VoteOption).filter(VoteOption.name=='Frånvarande').one()


member1 = aliased(Member)
member2 = aliased(Member)
vote1 = aliased(Vote)
vote2 = aliased(Vote)


# MAKE THIS SQL

# WITH pairs AS (SELECT m1.id AS p1, m2.id AS p2 FROM members AS m1 CROSS JOIN members AS m2 WHERE m1.id < m2.id)
# SELECT pairs.p1, pairs.p2, count(v1.poll_id)
# FROM (pairs INNER JOIN votes as v1 ON v1.member_id = p1) INNER JOIN votes as v2 ON v2.member_id=p2 AND v2.poll_id = v1.poll_id
# WHERE v1.vote_option_id = v2.vote_option_id
# GROUP BY pairs.p1,pairs.p2



for pair in s.query(member1.id,member2.id, func.count(vote1.poll_id))\
	.distinct(member1.id,member2.id) \
	.filter(member1.id != member2.id) \
	.filter(vote1.poll_id == vote2.poll_id) \
	.filter(vote1.member_id == member1.id) \
	.filter(vote2.member_id == member2.id) \
	.filter(vote1.vote_option_id == vote2.vote_option_id) \
	.filter(vote1.vote_option_id != absent_vote.id) \
	.filter(vote2.vote_option_id != absent_vote.id) \
	.group_by(vote1.poll_id) \
	.limit(10):

	print(pair)



exit()




for (m1,m2) in combinations(s.query(Member), 2):
	
	antal = s.query(vote1, vote2) \
		.filter(vote1.member_id == m1.id) \
		.filter(vote2.member_id == m2.id) \
		.filter(vote1.vote_option_id == vote2.vote_option_id) \
		.filter(vote1.vote_option_id != absent_vote.id) \
		.filter(vote2.vote_option_id != absent_vote.id) \
		.filter(vote1.poll_id == vote2.poll_id).count()
	print(('{} och {}: {}'.format(m1.id,m2.id,antal)))
