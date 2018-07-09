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
from itertools import permutations

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
    "FI",
    "JL",
    "FP",
    "L",
    "KD"
])}


def cosigning_timeseries():    
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
    

    riksmoten = ['{:04d}/{:02d}'.format(y,y-2000+1) for y in range(2002,2014)]

    output = dict()
    num_missing_committee_report = 0
    num_missing_committee_report_committee = 0

    matrix = dict()
    
    for (rm_idx, rm) in enumerate(riksmoten):
        print("RM: {}".format(rm))

        for doc in basequery.filter(MemberProposal.session == rm):

            if not doc.signatories or len(doc.signatories) == 1:
                continue

            signing_parties = sorted(list(set( m.party.id for m in doc.signatories if not m.party.abbr == "-")))
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

                # compute party matrix data
                for (p1,p2) in permutations(signing_parties,2):
                    if not p1 in matrix:
                        matrix[p1] = dict()

                    for committee_key in [0, committee.id]:
                        if not committee_key in matrix[p1]:
                            matrix[p1][committee_key] = dict()
                        if not p2 in matrix[p1][committee_key]:
                            matrix[p1][committee_key][p2] = dict(
                                    values = [0 for rm in riksmoten],
                                    abbr = party_metadata[p2]["abbr"],
                                    name = party_metadata[p2]["name"],
                                    id = p2
                                )
                        matrix[p1][committee_key][p2]["values"][rm_idx] += 1

                # compute timeseries data
                for committee_key in [0, committee.id]:
                    if not committee_key in output:
                        output[committee_key] = dict()

                    if not parties_key in output[committee_key]:
                        output[committee_key][parties_key] = \
                          dict(
                                values = [0 for rm in riksmoten],
                                abbr = ' + '.join(party_metadata[p_id]["abbr"] for p_id in signing_parties),
                                name = ' + '.join(party_metadata[p_id]["name"] for p_id in signing_parties),
                                num_parties = len(signing_parties)
                              )
                        
                    output[committee_key][parties_key]["values"][rm_idx] += 1


    ds = MongoDBDatastore()

    output_timeseries_top = dict(
                        t = riksmoten,
                        committees = [dict(
                        abbr = committee_metadata[c_id]["abbr"],
                        name = committee_metadata[c_id]["name"],
                        id = c_id,
                        series = [
                                    [dict(
                                        abbr=p_dict["abbr"],
                                        name=p_dict["name"],
                                        num_parties=p_dict["num_parties"],
                                        value=p_dict["values"][rm_idx]
                                        ) for (p_key, p_dict) in series.items() if p_dict["values"][rm_idx] > 0] 
                                      for (rm_idx, rm) in enumerate(riksmoten)
                                 ]
                        ) for (c_id, series) in output.items()]
                    )
    ds.store_object(output_timeseries_top,"party_cosigning_timeseries")


    mongodb = ds.get_mongodb_database() 
    mongo_collection = mongodb.party_cosigning_matrix
    mongo_collection.ensure_index([("partyA",ASCENDING)],unique=True)

    for (p1, matrix_p1) in matrix.items():
        mongo_partyA = party_metadata[p1]["abbr"]
        output_party_matrix_top = dict(
                            partyA = mongo_partyA,
                            t = riksmoten,
                            committees = [dict(
                            abbr = committee_metadata[c_id]["abbr"],
                            name = committee_metadata[c_id]["name"],
                            id = c_id,
                            parties = list(committee_dict.values())
                            ) for (c_id, committee_dict) in matrix_p1.items()]
                        )
        mongo_collection.update(dict(partyA = mongo_partyA), output_party_matrix_top, upsert=True)

        
    
    print("missing committee_report: {}, committee_reports missing committee's: {}".format(num_missing_committee_report,num_missing_committee_report_committee))

def main():
    cosigning_timeseries()
    
if __name__ == '__main__':
        main()     