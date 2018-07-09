from demokratikollen.core.db_structure import *
from sqlalchemy import create_engine, func, distinct, or_
from sqlalchemy.orm import sessionmaker, aliased, joinedload
from sqlalchemy.sql.expression import literal
from itertools import combinations
from demokratikollen.core.utils.mongodb import MongoDBDatastore
from demokratikollen.core.utils import postgres as pg_utils, riksdagen
import datetime as dt
import json
from pymongo import ASCENDING
from collections import defaultdict
import re
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
    "FI",
    "JL",
    "FP",
    "L",
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
    result_metadata = dict()
    result_metadata['bifall'] = dict(
            name= 'Bifall',
            ordering = 2
        )
    result_metadata['delvis bifall'] = dict(
            name= 'Delvis bifall',
            ordering = 1
        )
    result_metadata['avslag'] = dict(
            name= 'Avslag',
            ordering = 0
        )



    mdb = MongoDBDatastore()
    mongodb = mdb.get_mongodb_database() 
    mongo_collection = mongodb.proposals_main
    mongo_collection.ensure_index([("government", ASCENDING)], unique=True)

    mongo_collection_party_detail = mongodb.proposals_party_detail
    mongo_collection_party_detail.ensure_index([("government", ASCENDING),("party_id", ASCENDING)], unique=True)

    mongo_collection_committee_detail = mongodb.proposals_committee_detail
    mongo_collection_committee_detail.ensure_index([("government", ASCENDING),("committee_id", ASCENDING)], unique=True)

    mongo_collection_ministries_detail = mongodb.proposals_ministries_detail
    mongo_collection_ministries_detail.ensure_index([("government", ASCENDING)], unique=True)

    mongo_collection_multiparties_detail = mongodb.proposals_multiparties_detail
    mongo_collection_multiparties_detail.ensure_index([("government", ASCENDING)], unique=True)

    mongo_collection_members_detail = mongodb.proposals_members_detail
    mongo_collection_members_detail.ensure_index([("government", ASCENDING)], unique=True)

    basequery = s.query(Proposal).options( \
            joinedload(Proposal.points).joinedload(ProposalPoint.committee_report).joinedload(CommitteeReport.committee)) \
            .order_by(Proposal.published.desc())

    governments = [
        ("persson3",
        dict(title="Person III", years="2002-2006", party="S"), 
            basequery.filter(MemberProposal.session.in_(['2002/03', '2003/04', '2004/05', '2005/06'])) 
        ),
        ("reinfeldt1",
        dict(title="Reinfeldt I", years="2006-2010", party="M"), 
            basequery.filter(MemberProposal.session.in_(['2006/07', '2007/08', '2008/09', '2009/10'])) 
        ),
        ("reinfeldt2",
        dict(title="Reinfeldt II", years="2010-2014", party="M"),
            basequery.filter(MemberProposal.session.in_(['2010/11', '2011/12', '2012/13', '2013/14']))
        )
        ]

    
    num_missing_committee_report = 0
    num_missing_committee_report_committee = 0
    num_unknown_result = 0

    for (name, government_metadata, query) in governments:
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

                committee_key = committee.id
                result_key = result.lower()

                if not result_key in result_metadata.keys():
                    num_unknown_result += 1
                    print("Unknown result: {} {}".format(result_key, doc))

                    continue
                
                if not result_key in origin_tree[origin_key][committee_key]:
                    origin_tree[origin_key][committee_key][result_key] = list()
                
                origin_tree[origin_key][committee_key][result_key].append((doc.id, point.number))

                committees_set.add(committee_key)
                results_set.add(result_key)

        def party_sort_key(p):
            return party_metadata[p]['ordering']

        def result_sort_key(r):
            return result_metadata[r]['ordering']

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
        results.sort(key=result_sort_key)
        result_idc = {r:k for (k,r) in enumerate(results)}

        nodes = list()
        node_group_members = dict(
            title="Enskilda\nledamöters\nmotioner", 
            items=[dict(detail="members", title=p) for p in members],
            label = -1)

        node_group_party = dict(
            title="Partiernas\nmotioner", 
            items=[dict(detail="party", party_id=p, title=party_metadata[p]['name'],abbr=party_metadata[p]['abbr']) for p in parties],
            label = -1)

        node_group_multiparty = dict(
            title="Flerparti-\nmotioner", 
            items=[dict(detail="multiparties", title=p) for p in multiparties],
            label = -1)
        node_group_government = dict(
            title="Regeringens\npropositioner", 
            items=[dict(detail="government", title=p) for p in ministries],
            label = -1)

        node_group_committee = dict(
            title="Utskotten", 
            items=[dict(detail="committee",committee_id=p, title=committee_metadata[p]['name'],abbr=committee_metadata[p]['abbr']) for p in committees],
            label = 0)
        node_group_results = dict(
            title="Beslut", 
            items=[dict(detail="beslut", result_id=r, title=result_metadata[r]['name']) for r in results],
            label = 0)

        nodes = [
            dict(x=0.0, title='1. Förslag kommer från\nriksdagens ledamöter\noch regeringen', items=[node_group_members, node_group_party, node_group_multiparty, node_group_government]),
            dict(x=0.5, title='2. De bereds i ett\nav utskotten.', items=[node_group_committee]),
            dict(x=1.0, title='3. Beslut i\nriksdagens kammare.', items=[node_group_results])
        ]

        flows = list()
        for member_key in members_tree:
            for committee_key in members_tree[member_key]:
                for (result_key, point_ids) in members_tree[member_key][committee_key].items():
                    member_addr = (0,0,member_idc[member_key])
                    committee_addr = (1,0,committee_idc[committee_key])
                    result_addr = (2,0,result_idc[result_key])
                    flows.append(dict(path=[member_addr, committee_addr, result_addr], magnitude=len(point_ids)))

        for party_key in parties_tree:
            for committee_key in parties_tree[party_key]:
                for (result_key, point_ids) in parties_tree[party_key][committee_key].items():
                    party_addr = (0,1,party_idc[party_key])
                    committee_addr = (1,0,committee_idc[committee_key])
                    result_addr = (2,0,result_idc[result_key])
                    flows.append(dict(path=[party_addr, committee_addr, result_addr], magnitude=len(point_ids)))

        for multiparty_key in multiparties_tree:
            for committee_key in multiparties_tree[multiparty_key]:
                for (result_key, point_ids) in multiparties_tree[multiparty_key][committee_key].items():
                    multiparty_addr = (0,2,multiparty_idc[multiparty_key])
                    committee_addr = (1,0,committee_idc[committee_key])
                    result_addr = (2,0,result_idc[result_key])
                    flows.append(dict(path=[multiparty_addr, committee_addr, result_addr], magnitude=len(point_ids)))                    

        for ministry_key in ministries_tree:
            for committee_key in ministries_tree[ministry_key]:
                for (result_key, point_ids) in ministries_tree[ministry_key][committee_key].items():
                    ministry_addr = (0,3,ministry_idc[ministry_key])
                    committee_addr = (1,0,committee_idc[committee_key])
                    result_addr = (2,0,result_idc[result_key])
                    flows.append(dict(path=[ministry_addr, committee_addr, result_addr], magnitude=len(point_ids)))


        def parse_title(s,dbs):
            r = re.sub(r'med anledning av', 'm.a.a.', s)
            r = re.sub(r'([0-9]{4}/[0-9]{2}):(\S{,7})', lambda m: '<a href="{}">{}</a>'.format(riksdagen.url_from_code(m.group(1),m.group(2),dbs),m.group(0)), r)
            return r

        def author_string(doc):
            if len(doc.signatories)>2:
                return '{} och {} till'.format(repr(doc.signatories[0]),len(doc.signatories)-1)
            else:
                return ' och '.join(map(repr,doc.signatories))

        def shortest_number_string(l):
            items = []
            i = 0
            on_streak = False

            while i < len(l):
                if not on_streak:
                    start = i
    
                if len(l) == i+1 or l[i+1] != l[i]+1:
                    if start == i:
                        items.append(repr(l[start]))
                    else:
                        if i-start == 1:
                            items.append('{},{}'.format(repr(l[start]),repr(l[i])))
                        else:
                            items.append('{}-{}'.format(repr(l[start]),repr(l[i])))
                    on_streak = False
                else:
                    on_streak = True

                i += 1



            return ', '.join(items)

        def documents_from_points(decision_sets):
            result = list()
            prevdocid = 0
            row = None


            for (decision, ids) in decision_sets:
                for (docid, number) in ids:
                    if not (docid == prevdocid):
                        doc = s.query(Document).get(docid)
                        parsed_title = parse_title(doc.title,s)
                        authors = author_string(doc)
                        title_html = '<span class="authors">{}</span><span class="title">{}</span>'.format(authors, parsed_title)
                        row = dict(
                                decision=decision,
                                title=title_html, 
                                unique_code=doc.unique_code(),
                                url=riksdagen.url_from_dokid(doc.dok_id),
                                numbers='')
                        numbers = []
                        result.append(row)

                    numbers.append(number)
                    numbers.sort()
                    row['numbers'] = shortest_number_string(numbers)
                    prevdocid = docid



            return result

        def documents_from_prop(decision_sets):
            result = list()
            prevdocid = 0
            row = None


            for (decision, ids) in decision_sets:
                for (docid, number) in ids:
                    if not (docid == prevdocid):
                        doc = s.query(Document).get(docid)
                        parsed_title = parse_title(doc.title,s)
                        authors = "?"
                        if not doc.ministry is None:
                            authors = doc.ministry.name

                        title_html = '<span class="authors">{}</span><span class="title">{}</span>'.format(authors, parsed_title)
                        row = dict(
                                decision=decision,
                                title=title_html, 
                                unique_code=doc.unique_code(),
                                url=riksdagen.url_from_dokid(doc.dok_id),
                                numbers='')
                        numbers = []
                        result.append(row)

                    numbers.append(number)
                    numbers.sort()
                    row['numbers'] = shortest_number_string(numbers)
                    prevdocid = docid



            return result


        def committee_detail_for_tree(tree, doctype):

            total_bifall = 0
            total_delvis_bifall = 0
            total_avslag = 0

            committee_results = []
            for c_id in committees:
                if c_id not in tree:
                    continue    

                bifall_ids = tree[c_id].get('bifall',[])
                delvis_bifall_ids = tree[c_id].get('delvis bifall',[])
                avslag_ids = tree[c_id].get('avslag',[])
                num_bifall = len(bifall_ids)
                num_delvis_bifall = len(delvis_bifall_ids)
                num_avslag = len(avslag_ids)
                total_bifall += num_bifall
                total_delvis_bifall += num_delvis_bifall
                total_avslag += num_avslag
                
                all_ids = (("Bifall", bifall_ids), ("Delvis bifall", delvis_bifall_ids), ("Avslag", avslag_ids))
                doc_function = documents_from_points
                if doctype == 'government':
                    all_ids = all_ids[::-1]
                    doc_function = documents_from_prop

                committee_results.append({
                    'name': committee_metadata[c_id]['name'],
                    'abbr': committee_metadata[c_id]['abbr'],
                    'bifall': num_bifall,
                    'delvis_bifall': num_delvis_bifall,
                    'avslag': num_avslag,
                    'documents': doc_function(all_ids)
                })


            return dict(
                    committee_results = committee_results,
                    total_bifall = total_bifall,
                    total_delvis_bifall = total_delvis_bifall,
                    total_avslag = total_avslag
                )


        def origin_detail_for_tree(tree, doctype):
            origin_results = []

            bifall_ids = tree[c_id].get('bifall',[])
            delvis_bifall_ids = tree[c_id].get('delvis bifall',[])
            avslag_ids = tree[c_id].get('avslag',[])
            num_bifall = len(bifall_ids)
            num_delvis_bifall = len(delvis_bifall_ids)
            num_avslag = len(avslag_ids)

            all_ids = (("Bifall", bifall_ids), ("Delvis bifall", delvis_bifall_ids), ("Avslag", avslag_ids))
            doc_function = documents_from_points
            if doctype == 'government':
                all_ids = all_ids[::-1]
                doc_function = documents_from_prop    
                        
            return {
                'bifall': num_bifall,
                'delvis_bifall': num_delvis_bifall,
                'avslag': num_avslag,
                'documents': doc_function(all_ids)
                }


        print('Generating party_detail')
        party_detail = dict();
        for p_id in parties:
            committee_detail = committee_detail_for_tree(parties_tree[p_id], 'motion')
            committee_detail['party'] = party_metadata[p_id]
            party_detail[repr(p_id)] = committee_detail

        print('Generating ministries_detail')
        ministries_detail = committee_detail_for_tree(ministries_tree[ministries[0]], 'government')

        print('Generating members_detail')
        members_detail = committee_detail_for_tree(members_tree[members[0]],'motion')

        print('Generating multiparties_detail')
        multiparties_detail = committee_detail_for_tree(multiparties_tree[multiparties[0]],'motion')




        print('Generating committee_detail')
        committee_detail = dict();
        for c_id in committees:
            total_bifall = 0
            total_delvis_bifall = 0
            total_avslag = 0
            origin_results = []

            # government proposals first
            ret = origin_detail_for_tree(ministries_tree[ministries[0]], 'government')
            total_bifall += ret['bifall']
            total_delvis_bifall += ret['delvis_bifall']
            total_avslag += ret['avslag']
            ret.update(dict(
                    name='Regeringens propositioner',
                    abbr='R'
                ))
            origin_results.append(ret)

            # then members
            ret = origin_detail_for_tree(members_tree[members[0]], 'motion')
            total_bifall += ret['bifall']
            total_delvis_bifall += ret['delvis_bifall']
            total_avslag += ret['avslag']
            ret.update(dict(
                    name='Enskilda ledamöters motioner',
                    abbr='elm'
                ))
            origin_results.append(ret)

            # then multiparties
            ret = origin_detail_for_tree(multiparties_tree[multiparties[0]], 'motion')
            total_bifall += ret['bifall']
            total_delvis_bifall += ret['delvis_bifall']
            total_avslag += ret['avslag']
            ret.update(dict(
                    name='Samarbetsförslag',
                    abbr='sf'
                ))
            origin_results.append(ret)

            # finally parties
            for p_id in parties:
                if c_id not in parties_tree[p_id]:
                    continue

                ret = origin_detail_for_tree(parties_tree[p_id], 'motion')
                total_bifall += ret['bifall']
                total_delvis_bifall += ret['delvis_bifall']
                total_avslag += ret['avslag']
                ret.update(dict(
                        name=party_metadata[p_id]['name'],
                        abbr=party_metadata[p_id]['abbr']
                    ))
                origin_results.append(ret)

            committee_detail[repr(c_id)] = dict(
                committee = committee_metadata[c_id],
                origin_results = origin_results,
                total_bifall = total_bifall,
                total_delvis_bifall = total_delvis_bifall,
                total_avslag = total_avslag
                )


        output_top = dict(
                            government=name,
                            nodes = nodes,
                            flows = flows
                        )
        output_top.update(government_metadata)
        mongo_collection.update(dict(government=name), output_top, upsert=True)

        ministries_detail.update(dict(government=name))
        mongo_collection_ministries_detail.update(dict(government=name), ministries_detail, upsert=True)

        members_detail.update(dict(government=name))
        mongo_collection_members_detail.update(dict(government=name), members_detail, upsert=True)

        multiparties_detail.update(dict(government=name))
        mongo_collection_multiparties_detail.update(dict(government=name), multiparties_detail, upsert=True)

    
        for (p_id, d) in party_detail.items():
            d.update(dict(
                 government=name,party_id = p_id,   
                ))
            mongo_collection_party_detail.update(dict(government=name,party_id = p_id), d, upsert=True)
    
        for (c_id, d) in committee_detail.items():
            d.update(dict(
                 government=name,committee_id = c_id,   
                ))
            mongo_collection_committee_detail.update(dict(government=name,committee_id = c_id), d, upsert=True)

    print("missing committee_report: {}\ncommittee_reports missing committee's: {}\nunknown result: {}".format(num_missing_committee_report,num_missing_committee_report_committee,num_unknown_result))


if __name__ == '__main__':
        main()     