from db_structure import *
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.sql.expression import literal
from itertools import combinations
import utils

engine = create_engine(utils.engine_url())

session = sessionmaker(bind=engine)
s = session()


m1 = aliased(Member)
m2 = aliased(Member)
v1 = aliased(Vote)
v2 = aliased(Vote)
c = 0
for x in s.query(m1,m2,func.count(v1.poll_id))\
    .filter(m1.id == v1.member_id)\
    .filter(m2.id == v2.member_id)\
    .filter(m1.id < m2.id)\
    .filter(v1.poll_id == v2.poll_id)\
    .filter(v1.vote_option == v2.vote_option)\
    .filter(v1.vote_option != 'Frånvarande')\
    .filter(v2.vote_option != 'Frånvarande')\
    .group_by(m1.id,m2.id):

    c += 1
    print(x)
print (c)

# MAKE THIS SQL
# WITH pairs AS (SELECT m1.id AS p1, m2.id AS p2 FROM members AS m1 CROSS JOIN members AS m2 WHERE m1.id < m2.id)
# SELECT pairs.p1, pairs.p2, count(v1.poll_id)
# FROM (pairs INNER JOIN votes as v1 ON v1.member_id = p1) INNER JOIN votes as v2 ON v2.member_id=p2 AND v2.poll_id = v1.poll_id
# WHERE v1.vote_option_id = v2.vote_option_id
# GROUP BY pairs.p1,pairs.p2



#below this exit() is the a simpler brute-force way
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
