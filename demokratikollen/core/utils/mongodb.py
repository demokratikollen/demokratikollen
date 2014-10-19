from pymongo import MongoClient, ASCENDING
from urllib.parse import urlparse
import pickle
import os

def database_url():
    """returns mongo_database_url from env if it exists, otherwise default"""

    if 'MONGO_DATABASE_URL' in os.environ:
        return os.environ['MONGO_DATABASE_URL']
    else:
        return 'mongodb://localhost:27017/local'


class MongoDBDatastore:

    def __init__(self):
        self.dburl = database_url()
        
        url_comp = urlparse(self.dburl)
        database = url_comp.path[1:]
        
        self.connection = MongoClient(self.dburl)
        self.database = self.connection[database]
        self.collection = self.database.datastore
        self.collection.ensure_index([('identifier', ASCENDING)], unique=True)

    def get_mongodb_connection(self):
        return self.connection
       
    def get_mongodb_database(self):
        return self.database
    
    def get_mongodb_collection(self):
        return self.collection

    def store_string(self, json, identifier):
        object_to_store = {"identifier": identifier, "object": json}
        self.collection.update({"identifier": identifier}, object_to_store, upsert=True)

    def get_string(self, identifier):
        object_from_store = self.collection.find_one({'identifier': identifier})
        if object_from_store != None:
            return object_from_store['object']
        else:
            return None

    def store_object(self, object, identifier):
        obj_bytes = pickle.dumps(object)
        object_to_store = {"identifier": identifier, "object": obj_bytes}
        self.collection.update({"identifier": identifier}, object_to_store, upsert=True)
        
    def get_object(self, identifier):
        object_from_store = self.collection.find_one({'identifier': identifier})
        if object_from_store != None:
            return pickle.loads(object_from_store['object'])
        else:
            return None