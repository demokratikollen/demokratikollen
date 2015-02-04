from demokratikollen.www.app.helpers.db import db
from demokratikollen.www.app.helpers.cache import cache
from demokratikollen.core.db_structure import Party
from demokratikollen.core.utils.mongodb import MongoDBDatastore
import math

import datetime as dt
import calendar
import operator

mdb = MongoDBDatastore()

def party_comparator(p1):
    party_sort = {
        '-': 0,
        'v': 1,
        's': 2,
        'mp': 3,
        'sd': 4,
        'nyd': 5,
        'c': 6,
        'fp': 7,
        'kd': 8,
        'm': 9
    }
    return party_sort[p1.lower()]

db_name = {
        'c':'Centerpartiet',
        'fp':'Folkpartiet',
        'kd':'Kristdemokraterna',
        'mp':'Miljöpartiet',
        'm':'Moderaterna',
        's':'Socialdemokraterna',
        'sd':'Sverigedemokraterna',
        'v':'Vänsterpartiet'
    }

@cache.memoize(3600*24*30)
def party_election(party_abbr,year):
    party = db_name[party_abbr.lower()]
    year = str(year)

    el_dict = mdb.get_object("election_municipalities")
    el_totals = mdb.get_object("election_totals")
    el_party_sums = mdb.get_object("election_party_sums")

    el = el_dict[year][party]
    timeseries = el_party_sums[party]

    timeseries = {y: val/el_totals[y] for y,val in timeseries.items()}

    max_votes = max(el.values())

    out_dict = {"municipalities": [{"id": k, "votes": v} if not math.isnan(v) else {"id": k, "votes": 0} for k,v in el.items()]}
    out_dict["max_municipality"] = max_votes
    out_dict["history"] = timeseries

    return out_dict

@cache.memoize(3600*24*30)
def get_municipality_timeseries(party_abbr,m_id):
    party = db_name[party_abbr.lower()]
    m_id = str(m_id)

    el_dict = mdb.get_object("election_municipalities")
    timeseries = {"d": [{"year": y, "votes": dy[party][m_id]} for y,dy in sorted(el_dict.items(), key=operator.itemgetter(0)) if not math.isnan(dy[party][m_id])]}


    return timeseries

@cache.memoize(3600*24*30)
def get_best_party_gender(t,abbr):
    data = mdb.get_object("best_party_gender")
    if t == "latest":
        t = sorted(data.keys(),reverse=True)[0]

    out_data = data[t][abbr.lower()]
    for k,v in out_data.items():
        if math.isnan(v):
            out_data[k] = "NaN"

    return out_data

@cache.memoize(3600*24*30)
def get_best_party_education(t,abbr):
    data = mdb.get_object("best_party_education")
    if t == "latest":
        t = sorted(data.keys(),reverse=True)[0]

    out_data = data[t][abbr.lower()]
    for k,v in out_data.items():
        if math.isnan(v):
            out_data[k] = "NaN"

    return out_data