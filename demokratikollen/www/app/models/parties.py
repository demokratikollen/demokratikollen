from demokratikollen.www.app.helpers.db import db
from demokratikollen.core.db_structure import Party
from demokratikollen.core.utils.mongodb import MongoDBDatastore
import math

import datetime as dt
import calendar

mdb = MongoDBDatastore()

def party_bias(partyA_abbr, partyB_abbr):

    s=db.session
    A_id = s.query(Party.id).filter(Party.abbr==partyA_abbr).one()[0]
    B_id = s.query(Party.id).filter(Party.abbr==partyB_abbr).one()[0]

    mongodb = mdb.get_mongodb_database()
    mongo_collection = mongodb.party_covoting

    record= mongo_collection.find_one({"partyA": A_id, "partyB": B_id})
    del record['_id']
    return record


def party_election(party_abbr,year):
    party_abbr = party_abbr.lower()
    year = str(year)
    db_name = {
        'c':'Centerpartiet',
        'fp':'Folkpartiet',
        'kd':'Kristdemokraterna',
        'mp':'Miljöpartiet',
        'm':'Moderaterna',
        's':'Socialdemokraterna',
        'sd':'Sverigedemokraterna',
        'v':'Vänsterpartiet'
    }

    if party_abbr not in db_name:
        raise ValueError("Unknown party: {}".format(party_abbr))

    el_dict = mdb.get_object("election_data")
    try:
        el = el_dict[year][db_name[party_abbr]]
    except KeyError as e:
        raise ValueError("No election data for year {}.".format(year))

    max_votes = max(el.values())

    out_dict = {"d": [{"id": k, "votes": v} if not math.isnan(v) else {"id": k, "votes": 0} for k,v in el.items()]}
    out_dict["max_votes"] = max_votes

    return out_dict
