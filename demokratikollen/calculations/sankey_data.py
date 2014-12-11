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

def Tree(): return defaultdict(Tree)

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

    party_data = dict()
    for party in s.query(Party):
        party_data[party.id] = dict(
            abbr=party.abbr,
            ordering=party_ordering[party.abbr]
            )


    mdb = MongoDBDatastore()
    mongodb = mdb.get_mongodb_database() 
    mongo_collection = mongodb.proposals_main

    mongo_collection.ensure_index([("government", ASCENDING)], unique=True)


    basequery = s.query(Proposal).options( \
            joinedload(Proposal.points).joinedload(ProposalPoint.committee_report).joinedload(CommitteeReport.committee))

    governments = [
#        ("persson3"   , basequery.filter(MemberProposal.session.in_(['2002/03', '2003/04', '2004/05', '2005/06'])) ),
#        ("reinfeldt1" , basequery.filter(MemberProposal.session.in_(['2006/07', '2007/08', '2008/09', '2009/10'])) ),
        ("reinfeldt2" , basequery.filter(MemberProposal.session.in_(['2010/11', '2011/12', '2012/13', '2013/14'])) )
        ]

    
    num_missing_committee_report = 0
    num_missing_committee_report_committee = 0

    for (name, query) in governments:
        print("Government: {}".format(name))

        parties_tree = Tree()
        multiparties_tree = Tree()
        ministries_tree = Tree()
        members_tree = Tree()

        committees_set = set()
        results_set = set()



        for doc in query:

            if hasattr(doc, 'ministry_id'):

                origin_tree = ministries_tree
                origin_key = "Alla departement"

            else:

                if not doc.signatories or len(doc.signatories) == 0:
                    continue
                signing_parties = sorted(list(set( m.party.id for m in doc.signatories)))

                if doc.subtype == 'Enskild motion':
                    origin_tree = members_tree
                    origin_key = "Alla enskilda motioner"
                elif len(signing_parties) == 1:
                    origin_tree = parties_tree
                    origin_key = signing_parties[0]
                else: #multiparty signature
                    origin_tree = multiparties_tree
                    origin_key = "Alla Flerpartiförslag"


            for point in doc.points:
                if not point.committee_report:
                    print('Missing committee_report: {}, {}'.format(doc, point.number))
                    num_missing_committee_report += 1
                    continue
                if not point.committee_report.committee:
                    print('Missing committee_report.committee: {}, {}'.format(doc, point.number))
                    num_missing_committee_report_committee += 1
                    continue

                committee = point.committee_report.committee
                result = point.decision

                if not result.lower() in ['bifall','delvis bifall','avslag']:
                    continue

                committee_key = committee.id
                result_key = result
                
                if not result_key in origin_tree[origin_key][committee_key]:
                    origin_tree[origin_key][committee_key][result_key] = 0
                
                origin_tree[origin_key][committee_key][result_key] += 1

                committees_set.add(committee_key)
                results_set.add(result_key)

        def party_sort_key(p):
            return party_data[p]['ordering']

        parties = list(parties_tree.keys())
        parties.sort(key=party_sort_key)
        party_idc = {p:k for (k,p) in enumerate(parties)}

        multiparties = list(multiparties_tree.keys())
        multiparty_idc = {p:k for (k,p) in enumerate(multiparties)}

        ministries = list(ministries_tree.keys())
        ministry_idc = {p:k for (k,p) in enumerate(ministries)}

        members = list(members_tree.keys())
        member_idc = {p:k for (k,p) in enumerate(members)}


        committees = list(committees_set)
        committee_idc = {c:k for (k,c) in enumerate(committees)}

        results = list(results_set)
        result_idc = {r:k for (k,r) in enumerate(results)}

        nodes = list()

        node_group_members = dict(
            title="Enskilda ledamöters förslag", 
            items=[dict(title=p) for p in members],
            label = -1)

        node_group_party = dict(
            title="Partiförslag", 
            items=[dict(party_id=p, title=party_data[p]['abbr']) for p in parties],
            label = -1)

        node_group_multiparty = dict(
            title="Flerpartiförslag", 
            items=[dict(title=p) for p in multiparties],
            label = -1)
        node_group_government = dict(
            title="Regeringspropositioner", 
            items=[dict(title=p) for p in ministries],
            label = -1)

        node_group_committee = dict(
            title="Utskotten", 
            items=[dict(title=p) for p in committees],
            label = 0)
        node_group_results = dict(
            title="Besluten", 
            items=[dict(title=p) for p in results],
            label = 0)

        nodes = [
            dict(x=0.0, items=[node_group_members, node_group_party, node_group_multiparty, node_group_government]),
            dict(x=0.5, items=[node_group_committee]),
            dict(x=1.0, items=[node_group_results])
        ]

        flows = list()
        for member_key in members_tree:
            for committee_key in members_tree[member_key]:
                for (result_key, count) in members_tree[member_key][committee_key].items():
                    member_addr = (0,0,member_idc[member_key])
                    committee_addr = (1,0,committee_idc[committee_key])
                    result_addr = (2,0,result_idc[result_key])
                    flows.append(dict(path=[member_addr, committee_addr, result_addr], magnitude=count))

        for party_key in parties_tree:
            for committee_key in parties_tree[party_key]:
                for (result_key, count) in parties_tree[party_key][committee_key].items():
                    party_addr = (0,1,party_idc[party_key])
                    committee_addr = (1,0,committee_idc[committee_key])
                    result_addr = (2,0,result_idc[result_key])
                    flows.append(dict(path=[party_addr, committee_addr, result_addr], magnitude=count))

        for multiparty_key in multiparties_tree:
            for committee_key in multiparties_tree[multiparty_key]:
                for (result_key, count) in multiparties_tree[multiparty_key][committee_key].items():
                    multiparty_addr = (0,2,multiparty_idc[multiparty_key])
                    committee_addr = (1,0,committee_idc[committee_key])
                    result_addr = (2,0,result_idc[result_key])
                    flows.append(dict(path=[multiparty_addr, committee_addr, result_addr], magnitude=count))                    

        for ministry_key in ministries_tree:
            for committee_key in ministries_tree[ministry_key]:
                for (result_key, count) in ministries_tree[ministry_key][committee_key].items():
                    ministry_addr = (0,3,ministry_idc[ministry_key])
                    committee_addr = (1,0,committee_idc[committee_key])
                    result_addr = (2,0,result_idc[result_key])
                    flows.append(dict(path=[ministry_addr, committee_addr, result_addr], magnitude=count))



        output_top = dict(
                            government=name,
                            nodes = nodes,
                            flows = flows
                        )

        mongo_collection.update(dict(government=name), output_top, upsert=True)
    
    print("missing committee_report: {}, committee_reports missing committee's: {}".format(num_missing_committee_report,num_missing_committee_report_committee))


if __name__ == '__main__':
        main()     