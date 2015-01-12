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
from collections import Counter

def main():
    
    engine = create_engine(pg_utils.engine_url())
    session = sessionmaker(bind=engine)
    s = session() 


    # Enumerate all searchable objects and arrange in groups
    members = list()
    member_indices = dict()
    for (idx, member) in enumerate(s.query(Member)):
        members.append(dict(
                title = member.first_name + " " + member.last_name + " (" + member.party.abbr + ")",
                img_url = member.image_url_sm,
                url = '/'+member.url_name
            ))
        member_indices[member.id] = idx

    parties = list()
    party_indices = dict()
    for (idx, party) in enumerate(s.query(Party)):
        parties.append(dict(
                title = party.name,
                img_url = '/static/img/parties/'+party.abbr.lower()+'.png',
                url = '/'+party.abbr.lower()
            ))
        party_indices[party.id] = idx

    output_groups = [
        dict(title="Ledamöter", objects=members), dict(title="Partier", objects=parties)
    ]
    group_indices = dict(member=0, party=1)



    # Enumerate all strings to match and couple them to objects (primary and secondary hits)
    keywords = list()
    for member in s.query(Member):
        normalized_string = (member.first_name + " " + member.last_name).lower()
        keywords.append(dict(
                string = normalized_string,
                primary = (group_indices["member"], member_indices[member.id]),
                secondaries = [
                        (group_indices["party"], party_indices[member.party.id])
                    ]
            ))
    for party in s.query(Party):
        normalized_string = (party.name).lower()
        keywords.append(dict(
                string = normalized_string,
                primary = (group_indices["party"], party_indices[party.id]),
                secondaries = [
                        (group_indices["member"], member_indices[m.id]) for m in party.members[0:2]
                    ]
            ))

    # Generate reverse table of all trigrams to match, such that we can ask:
    # which keywords contain this trigram (and how many)

    trigrams_dict = dict()
    for (keyword_idx, keyword) in enumerate(keywords):
        grams = Counter(map(lambda t: ''.join(t), zip(*[keyword["string"][k:] for k in range(3)])))
        for (gram, count) in grams.items():
            if not gram in trigrams_dict:
                trigrams_dict[gram] = list()
            trigrams_dict[gram].append( (keyword_idx, count) )


    print('# unique trigrams: {}'.format(len(trigrams_dict)))



    output_top = dict(
            groups = output_groups,
            keywords = keywords
            )

    ds = MongoDBDatastore()
    ds.store_object(output_top,"search") 



if __name__ == '__main__':
        main()     