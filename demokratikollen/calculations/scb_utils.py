from collections import defaultdict
import urllib.request
import json

na_val = '..'

codes = {
    "Kon": {
        "codes": {
            "1": "Män",
            "2": "Kvinnor",
            "TOT": "Totalt"
        },
        "name": "Kön"
    },
    "UtbNivaSUN2000": {
        "codes": {
            "F": "Förgymnasial utbildning",
            "3": "Gymnasial utbildning",
            "K": "Eftergymnasial utbildning mindre än 3 år",
            "L": "Eftergymnasial utbildning 3 år eller mer",
            "9": "Okänd utbildning",
            "TOT": "Totalt"
        },
        "name": "Utbildningsnivå"
    },
    "Partisympati": {
        "codes": {
            "m":"m",
            "c":"c",
            "fp":"fp",
            "kd":"kd",
            "nyd":"nyd",
            "mp":"mp",
            "s":"s",
            "v":"v",
            "SD":"sd",
            "övr":"Övriga"
        },
        "name": "Partisympati"
    }

}

best_party_gender_key_order = ["Kon","UtbNivaSUN2000","Partisympati","Tid"]

class NestedDefaultdict(defaultdict):
    def __init__(self):
        super(NestedDefaultdict, self).__init__(NestedDefaultdict)

    def __repr__(self):
        return dict.__repr__(self)

    def to_dict(self):
        dictself = dict(self)
        for k,v in dictself.items():
            if isinstance(v,NestedDefaultdict):
                dictself[k] = v.to_dict()
        return dictself

def translate_keys(keys,key_order=best_party_gender_key_order):
    ko = dict(zip(keys,key_order))
    return [codes[scb_k]["codes"][k] if scb_k in codes else k for k,scb_k in zip(keys,key_order)]

def get_request(url,query):
    query_bytes = json.dumps(query).encode('utf-8')

    req = urllib.request.Request(url, query_bytes, {'Content-Type': 'application/json'})

    f = urllib.request.urlopen(req)
    response_str = f.read().decode('utf-8-sig')
    f.close()

    return json.loads(response_str)