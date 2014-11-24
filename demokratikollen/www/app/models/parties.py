from demokratikollen.www.app.helpers.db import db
from demokratikollen.core.db_structure import Party
from demokratikollen.core.utils.mongodb import MongoDBDatastore

import datetime as dt
import calendar

def party_bias(partyA_abbr, partyB_abbr):

    s=db.session
    A_id = s.query(Party.id).filter(Party.abbr==partyA_abbr).one()[0]
    B_id = s.query(Party.id).filter(Party.abbr==partyB_abbr).one()[0]

    mdb = MongoDBDatastore()
    mongodb = mdb.get_mongodb_database() 
    mongo_collection = mongodb.party_covoting

    record= mongo_collection.find_one({"partyA": A_id, "partyB": B_id})
    del record['_id']
    return record

