# coding=utf-8
import scb_utils as scb
from demokratikollen.core.utils.mongodb import MongoDBDatastore

QUERY = {
    "query": [
        {
            "code": "Region",
            "selection": {
                "filter": "vs:RegionValkretsTot99",
                "values": [
                    "VR00"
                ]
            }
        },
        {
            "code": "ContentsCode",
            "selection": {
                "filter": "item",
                "values": [
                    "ME0104B7"
                ]
            }
        }
    ],
    "response": {
        "format": "json"
    }
}


URL = "http://api.scb.se/OV0104/v1/doris/sv/ssd/START/ME/ME0104/ME0104C/ME0104T3"

def main():
    d = scb.get_request(URL, QUERY)

    out_data = scb.NestedDefaultdict()

    for entry in d["data"]:
        val = entry["values"][0]
        if val == scb.na_val:
            continue
        val = float(val)/100    
        party_abbr = entry["key"][1].lower()
        year = int(entry["key"][2])
        out_data[party_abbr][year] = val

    ds = MongoDBDatastore()
    ds.store_object(out_data.to_dict(), "election_results")

if __name__ == '__main__':
    main()
