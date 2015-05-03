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
    if record is None:
        raise KeyError
    
    del record['_id']
    return record


def party_detail(government, party_id):
    mdb = MongoDBDatastore()
    mongodb = mdb.get_mongodb_database() 
    mongo_collection = mongodb.proposals_party_detail

    record= mongo_collection.find_one({"government": government,'party_id': repr(party_id)})
    
    if record is None:
        raise KeyError
    del record['_id']
    return record

def ministries_detail(government):
    mdb = MongoDBDatastore()
    mongodb = mdb.get_mongodb_database() 
    mongo_collection = mongodb.proposals_ministries_detail

    print(mongo_collection)
    record= mongo_collection.find_one({"government": government})
    
    if record is None:
        raise KeyError
    del record['_id']
    return record
