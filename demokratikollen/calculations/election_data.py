import gzip
import json
import os
from demokratikollen.core.utils.mongodb import MongoDBDatastore

data_dir = '../data/other/'
in_file = os.path.join(data_dir,'elections.json.gz')

with gzip.open(in_file,'rt') as f:
    elec_dict = json.load(f)

ds = MongoDBDatastore()
ds.store_object(elec_dict,"election_data")
