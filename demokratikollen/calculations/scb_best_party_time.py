import scb_utils as scb
from demokratikollen.core.utils.mongodb import MongoDBDatastore

query = {
  "query": [
    {
      "code": "Kon",
      "selection": {
        "filter": "item",
        "values": [
          "TOT"
        ]
      }
    },
    {
      "code": "UtbNivaSUN2000",
      "selection": {
        "filter": "item",
        "values": [
          "TOT"
        ]
      },
    },
    {
      "code": "ContentsCode",
      "selection": {
        "filter": "item",
        "values": [
          "ME0201AV"
        ]
      }
    }
  ],
  "response": {
    "format": "json"
  }
}


url = "http://api.scb.se/OV0104/v1/doris/sv/ssd/START/ME/ME0201/ME0201B/Partisympati17"
d = scb.get_request(url,query)

data = scb.NestedDefaultdict()
key_order = scb.best_party_gender_key_order


for entry in d["data"]:
    val = entry["values"][0]
    val = float('NaN') if val==scb.na_val else float(val)/100
    keys = scb.translate_keys(entry["key"])

    keys_d = dict(zip(key_order,keys))
    t = keys_d["Tid"]
    p = keys_d["Partisympati"]

    data[p][t] = val


ds = MongoDBDatastore()
ds.store_object(data.to_dict(),"best_party_time")
