from demokratikollen.www.app.helpers.db import db
from demokratikollen.core.db_structure import Party
from demokratikollen.core.utils.mongodb import MongoDBDatastore

import datetime as dt
import calendar

def proposals_main(government):

    mdb = MongoDBDatastore()
    mongodb = mdb.get_mongodb_database() 
    mongo_collection = mongodb.proposals_main

    record= mongo_collection.find_one({"government": government})
    del record['_id']
    return record

def cosigning_matrix(party_abbr):

    ds = MongoDBDatastore()
    mongodb = ds.get_mongodb_database() 
    mongo_collection = mongodb.party_cosigning_matrix
    
    record= mongo_collection.find_one({"partyA": party_abbr})
    if record:
        del record['_id']
    return record

