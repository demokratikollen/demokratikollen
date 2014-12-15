import gzip
import json
import os
import math
from demokratikollen.core.utils.mongodb import MongoDBDatastore

cd = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(cd,'../data/other/')
in_file = os.path.join(data_dir,'elections.json.gz')

with gzip.open(in_file,'rt') as f:
    elec_dict = json.load(f)

sort_special = {
    "ej röstande": "did_not_vote",
    "ogiltiga valsedlar": "invalid",
}

municipalities = {}
party_sums = {}

print("Calculating election data.")

for y,dy in elec_dict.items():
    for p,dp in dy.items():

        # Sum over all municipalities for each party (ignore NaNs)
        if p not in party_sums:
            party_sums[p] = {}
        party_sums[p][y] = sum(v for v in dp.values() if not math.isnan(v))

        # Sum over parties and create
        # municipalities[id][year][{total_votes,did_not_vote,invalid}]: <number>
        for m in dp.keys():
            if m not in municipalities:
                municipalities[m] = {}
            if y not in municipalities[m]:
                municipalities[m][y] = {}
                municipalities[m][y]['total_votes'] = 0
            if p in sort_special:
                municipalities[m][y][sort_special[p]] = dp[m]
            else:
                if not math.isnan(dp[m]):
                    municipalities[m][y]['total_votes'] += dp[m]

totals = {}
for p,dp in party_sums.items():
    for y,val in dp.items():
        if y not in totals:
            totals[y] = 0
        totals[y] += val

# Set municipalities relative to number of votes (leave NaNs)
for y,dy in elec_dict.items():
    for p,dp in dy.items():
        for m in dp.keys():
            try:
                if not math.isnan(dp[m]):
                    dp[m] = dp[m]/municipalities[m][y]['total_votes']
            except ZeroDivisionError as e:
                print("Division by zero: municipality {}, year {}.".format(m,y))

print("Storing in MongoDB.")

ds = MongoDBDatastore()
ds.store_object(elec_dict,"election_municipalities")
ds.store_object(municipalities,"election_municipality_sums")
ds.store_object(party_sums,"election_party_sums")
ds.store_object(totals,"election_totals")
