from demokratikollen.core.db_structure import *
from sqlalchemy import create_engine, func, distinct, or_
from sqlalchemy.orm import sessionmaker, aliased, joinedload
from sqlalchemy.sql.expression import literal
from itertools import combinations
from demokratikollen.core.utils.mongodb import MongoDBDatastore
from demokratikollen.core.utils import postgres as pg_utils
import datetime as dt
import json
from pymongo import ASCENDING
from collections import defaultdict

party_ordering = {p: i for (i, p) in enumerate([
    "V",
    "PP",
    "MP",
    "S",
    "SD",
    "NYD",
    "-",
    "C",
    "M",
    "FP",
    "KD"
])}

def main():
    
    engine = create_engine(pg_utils.engine_url())
    session = sessionmaker(bind=engine)
    s = session() 

    party_metadata = dict()
    for party in s.query(Party):
        party_metadata[party.id] = dict(
            abbr=party.abbr,
            name=party.name,
            ordering=party_ordering[party.abbr]
            )
    committee_metadata = dict()
    for c in s.query(Committee):
        committee_metadata[c.id] = dict(
                abbr=c.abbr,
                name=c.name
            )
    committee_metadata[0] = dict(
                abbr="Alla",
                name="Alla utskott"
                )



    basequery = s.query(MemberProposal) \
                    .options(joinedload(MemberProposal.points).joinedload(ProposalPoint.committee_report).joinedload(CommitteeReport.committee)) \
                    .filter(MemberProposal.subtype != 'Enskild motion')
    

    riksmoten = ['{:04d}/{:02d}'.format(y,y-2000+1) for y in range(2002,2005)]

    output = dict()
    num_missing_committee_report = 0
    num_missing_committee_report_committee = 0
    
    for (rm_idx, rm) in enumerate(riksmoten):
        print("RM: {}".format(rm))

        for doc in basequery.filter(MemberProposal.session == rm):

            if not doc.signatories or len(doc.signatories) == 1:
                continue

            signing_parties = sorted(list(set( m.party.id for m in doc.signatories)))
            if len(signing_parties) <= 1:
                continue

            parties_key = repr(signing_parties)

            for point in doc.points:
                if not point.committee_report:
                    num_missing_committee_report += 1
                    continue
                if not point.committee_report.committee:
                    num_missing_committee_report_committee += 1
                    continue



                committee = point.committee_report.committee

                for committee_key in [0, committee.id]:
                    if not committee_key in output:
                        output[committee_key] = dict()

                    if not parties_key in output[committee_key]:
                        output[committee_key][parties_key] = \
                          dict(
                                values = [0 for rm in riksmoten],
                                abbr = ' + '.join(party_metadata[p_id]["abbr"] for p_id in signing_parties),
                                name = ' + '.join(party_metadata[p_id]["name"] for p_id in signing_parties)
                              )
                        
                    output[committee_key][parties_key]["values"][rm_idx] += 1


    output_top = dict(
                        t = riksmoten,
                        committees = [dict(
                        abbr = committee_metadata[c_id]["abbr"],
                        name = committee_metadata[c_id]["name"],
                        series = list(series.values())
                        ) for (c_id, series) in output.items()]
                    )

        
    ds = MongoDBDatastore()
    ds.store_object(output_top,"party_cosigning_timeseries")
    
    print("missing committee_report: {}, committee_reports missing committee's: {}".format(num_missing_committee_report,num_missing_committee_report_committee))


if __name__ == '__main__':
        main()     