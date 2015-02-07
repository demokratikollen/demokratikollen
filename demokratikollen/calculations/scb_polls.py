# coding=utf-8
import scb_utils as scb
import datetime as dt
from demokratikollen.core.utils.mongodb import MongoDBDatastore

QUERY = {
    "query": [
        {
            "code": "ContentsCode",
            "selection": {
                "filter": "item",
                "values": [
                    "ME0201B1"
                ]
            }
        }
    ],
    "response": {
        "format": "json"
    }
}


URL = "http://api.scb.se/OV0104/v1/doris/sv/ssd/START/ME/ME0201/ME0201A/Vid10"

def main():
    d = scb.get_request(URL, QUERY)

    out_data = scb.NestedDefaultdict()

    for entry in d["data"]:
        val = entry["values"][0]
        if val == scb.na_val:
            continue
        val = float(val)/100    
        party_abbr = entry["key"][0].lower()
        year, month = map(int, entry["key"][1].split('M'))
        day = 1
        date = dt.datetime(year, month, day)
        out_data[party_abbr][date] = val

    ds = MongoDBDatastore()
    ds.store_object(out_data.to_dict(), "scb_polls")

if __name__ == '__main__':
    main()
