from demokratikollen.core.db_structure import *
from sqlalchemy import create_engine, func, distinct, or_
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.sql.expression import literal
from itertools import combinations
from demokratikollen.core.utils.mongodb import MongoDBDatastore
from demokratikollen.core.utils import postgres as pg_utils
import datetime as dt
import json
from pymongo import ASCENDING
from copy import deepcopy
def main():
    
    engine = create_engine(pg_utils.engine_url())
    session = sessionmaker(bind=engine)
    s = session() 

    riksmoten = ['{:04d}/{:02d}'.format(y,y-2000+1) for y in range(2002,2014)]

    parties = s.query(Party) \
                .filter(Party.abbr != "-") \
                .order_by(Party.id)

    v1 = aliased(PartyVote)
    v2 = aliased(PartyVote)
    v3 = aliased(PartyVote)

    mdb = MongoDBDatastore()
    mongodb = mdb.get_mongodb_database() 
    mongo_collection = mongodb.party_covoting
    mongo_collection.ensure_index([("partyA",ASCENDING),("partyB",ASCENDING)],unique=True)

    for (partyA, partyB) in combinations(parties, 2):

        conflicting_votes = s.query(v1, v2) \
                                .filter(v1.polled_point_id == v2.polled_point_id) \
                                .filter(v1.party_id == partyA.id) \
                                .filter(v2.party_id == partyB.id) \
                                .filter(or_(v1.vote_option == 'Ja', v1.vote_option == 'Nej')) \
                                .filter(or_(v2.vote_option == 'Ja', v2.vote_option == 'Nej')) \
                                .filter(v1.vote_option != v2.vote_option)
        
        num_conflicting = conflicting_votes.count()
        if num_conflicting < 1000:
            continue

        print('================================')
        print('{} vs {}: {} conflicting votes'.format(partyA.abbr,partyB.abbr, num_conflicting))

        output_parties = list()
        for party in parties:
            agree_query = s.query(v1, v2, v3, PolledPoint,CommitteeReport).join(CommitteeReport,PolledPoint.report)\
                                .filter(PolledPoint.id == v1.polled_point_id) \
                                .filter(v1.polled_point_id == v2.polled_point_id) \
                                .filter(v1.party_id == partyA.id) \
                                .filter(v2.party_id == partyB.id) \
                                .filter(or_(v1.vote_option == 'Ja', v1.vote_option == 'Nej')) \
                                .filter(or_(v2.vote_option == 'Ja', v2.vote_option == 'Nej')) \
                                .filter(v1.vote_option != v2.vote_option) \
                                .filter(v3.polled_point_id == v2.polled_point_id) \
                                .filter(v3.party_id == party.id)

            party_bias = list()
            for (rm_idx, rm) in enumerate(riksmoten):

                agree_query_interval = agree_query.filter(CommitteeReport.session == rm)

                agreeA = agree_query_interval.filter(v3.vote_option == v1.vote_option).count()
                agreeB = agree_query_interval.filter(v3.vote_option == v2.vote_option).count()
                print(agreeA)
                print(agreeB)
                if agreeA + agreeB > 0:
                    party_bias.append( float(agreeB - agreeA)/float(agreeA + agreeB))
                else:
                    party_bias.append( float('NaN'))

            print('{}...'.format(party.abbr))
            output_parties.append(dict(
                                        party_id=party.id,
                                        party_abbr=party.abbr,
                                        party_name=party.name,
                                        values=party_bias)) 
        
        print('Dumping to MongoDB.')
        output_parties_reverse = deepcopy(output_parties)
        for item in output_parties_reverse:
            item['values'] = [-x for x in item['values']]


        output_top = dict(partyA = partyA.id, partyB = partyB.id, series = output_parties,labels=riksmoten)
        output_top_reverse = dict(partyA = partyB.id, partyB = partyA.id, series = output_parties_reverse, labels=riksmoten)
        mongo_collection.update(dict(partyA = partyA.id, partyB = partyB.id), output_top, upsert=True)
        mongo_collection.update(dict(partyA = partyB.id, partyB = partyA.id), output_top_reverse, upsert=True)


if __name__ == '__main__':
        main()     