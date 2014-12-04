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
from collections import defaultdict


def main():
    
    engine = create_engine(pg_utils.engine_url())
    session = sessionmaker(bind=engine)
    s = session() 

    mdb = MongoDBDatastore()
    mongodb = mdb.get_mongodb_database() 
    mongo_collection = mongodb.proposals_main

    mongo_collection.ensure_index([("government", ASCENDING)], unique=True)


    basequery = s.query(MemberProposal) \
        .filter('Enskild motion' != MemberProposal.subtype)

    governments = [
        ("persson3"   , basequery.filter(MemberProposal.session.in_(['2002/03', '2003/04', '2004/05', '2005/06']))),
        ("reinfeldt1" , basequery.filter(MemberProposal.session.in_(['2006/07', '2007/08', '2008/09', '2009/10']))),
        ("reinfeldt2" , basequery.filter(MemberProposal.session.in_(['2010/11', '2011/12', '2012/13', '2013/14'])))
        ]

    def add_unique(l, i):
        if not i in l:
            l.append(i)
            return len(l)-1
        else:
            return l.index(i)

    for (name, query) in governments:
        print("Government: {}".format(name))
        parties = list()
        committees = list()
        results = list()

        links_parties_committees = defaultdict(int)
        links_committees_results = defaultdict(int)

        parties_values = defaultdict(int)
        committees_values = defaultdict(int)
        results_values = defaultdict(int)

        for doc in query:
            if not doc.signatories or len(doc.signatories) == 0:
                continue

            signing_parties = sorted(list(set( m.party.id for m in doc.signatories)))
            signing_members = list(m.id for m in doc.signatories)
            
            parties_key = repr(signing_parties)
            parties_idx = add_unique(parties, parties_key)

            for point in doc.points:
                if not point.committee_report:
                    #print('Missing committee_report: {}, {}'.format(doc, point.number))
                    continue
                if not point.committee_report.committee:
                    #print('Missing committee_report.committee: {}, {}'.format(doc, point.number))
                    continue
                committee = point.committee_report.committee

                committee_key = committee.id
                result_key = point.decision
                committee_idx = add_unique(committees, committee_key)
                result_idx = add_unique(results, result_key)

                links_parties_committees[(parties_idx, committee_idx)] += 1
                links_committees_results[(committee_idx, result_idx)] += 1

                parties_values[parties_key] += 1
                committees_values[committee_key] += 1
                results_values[result_key] += 1


        output_top = dict(
                            government=name,
                            parties = [dict(name=p, value=parties_values[p]) for p in parties],
                            committees = [dict(name=c, value = committees_values[c])  for c in committees],
                            results = [dict(name=r, value=results_values[r]) for r in results],
                            links_parties_committees = [dict(origin=fr,committee=to,val=val) for ((fr,to) , val) in links_parties_committees.items()],
                            links_committees_results = [dict(committee=fr,result=to,val=val) for ((fr,to) , val) in links_committees_results.items()]
                        )

        mongo_collection.update(dict(government=name), output_top, upsert=True)
        


if __name__ == '__main__':
        main()     