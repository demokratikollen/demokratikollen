from demokratikollen.core.db_structure import *
from sqlalchemy import create_engine, func, distinct, or_
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.sql.expression import literal
from itertools import combinations
from demokratikollen.core.utils import postgres as pg_utils
import datetime as dt

def main():
    
    engine = create_engine(pg_utils.engine_url())
    session = sessionmaker(bind=engine)
    s = session() 

    intervals = [] 

    for y in range(2002,2015):
        intervals.append( (dt.date(y,1,1), dt.date(y,7,1)) )
        intervals.append( (dt.date(y,7,1), dt.date(y+1,1,1)) )

    parties = s.query(Party) \
                .filter(Party.abbr != "-") \
                .order_by(Party.id)

    v1 = aliased(PartyVote)
    v2 = aliased(PartyVote)
    v3 = aliased(PartyVote)

    for (partyA, partyB) in combinations(parties, 2):
        
        
        conflicting_votes = s.query(v1, v2) \
                                .filter(v1.polled_point_id == v2.polled_point_id) \
                                .filter(v1.party_id == partyA.id) \
                                .filter(v2.party_id == partyB.id) \
                                .filter(or_(v1.vote_option == 'Ja', v1.vote_option == 'Nej')) \
                                .filter(or_(v2.vote_option == 'Ja', v2.vote_option == 'Nej')) \
                                .filter(v1.vote_option != v2.vote_option)
        
        num_conflicting = conflicting_votes.count()
        if num_conflicting < 100:
            continue

        print('================================')
        print('{} vs {}: {} conflicting votes'.format(partyA.abbr,partyB.abbr, num_conflicting))

        for party in parties:
            agree_query = s.query(v1, v2, v3, PolledPoint) \
                                .filter(PolledPoint.id == v1.polled_point_id) \
                                .filter(v1.polled_point_id == v2.polled_point_id) \
                                .filter(v1.party_id == partyA.id) \
                                .filter(v2.party_id == partyB.id) \
                                .filter(or_(v1.vote_option == 'Ja', v1.vote_option == 'Nej')) \
                                .filter(or_(v2.vote_option == 'Ja', v2.vote_option == 'Nej')) \
                                .filter(v1.vote_option != v2.vote_option) \
                                .filter(v3.polled_point_id == v2.polled_point_id) \
                                .filter(v3.party_id == party.id)

            party_biases = [None for interval in intervals]
            for (k, interval) in enumerate(intervals):

                agree_query_interval = agree_query.filter(PolledPoint.poll_date >= interval[0], PolledPoint.poll_date < interval[1])

                agreeA = agree_query_interval.filter(v3.vote_option == v1.vote_option).count()
                agreeB = agree_query_interval.filter(v3.vote_option == v2.vote_option).count()

                if agreeA + agreeB > 0:
                    party_biases[k] = float(agreeB - agreeA)/float(agreeA + agreeB)
            
            print('{}: {}'.format(party.abbr, party_biases))



if __name__ == '__main__':
        main()     