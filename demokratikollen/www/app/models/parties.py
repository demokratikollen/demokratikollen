from demokratikollen.www.app.helpers.db import db
from demokratikollen.www.app.helpers.cache import cache
from demokratikollen.core.db_structure import Party, Group, GroupAppointment, Member
from demokratikollen.core.utils.mongodb import MongoDBDatastore
import math

import datetime as dt
import calendar
import operator

mdb = MongoDBDatastore()

# From se.wikipedia.org...
ELECTION_DATES = {
    1973: dt.datetime(1973, 9, 16),
    1976: dt.datetime(1976, 9, 19),
    1979: dt.datetime(1979, 9, 16),
    1982: dt.datetime(1982, 9, 19),
    1985: dt.datetime(1985, 9, 15),
    1988: dt.datetime(1988, 9, 18),
    1991: dt.datetime(1991, 9, 15),
    1994: dt.datetime(1994, 9, 18),
    1998: dt.datetime(1998, 9, 20),
    2002: dt.datetime(2002, 9, 15),
    2006: dt.datetime(2006, 9, 17),
    2010: dt.datetime(2010, 9, 19),
    2014: dt.datetime(2014, 9, 14),
    2018: dt.datetime(2018, 9, 9)    
}

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
def party_election_history(party_abbr):
    party = db_name[party_abbr.lower()]

    el_totals = mdb.get_object("election_totals")
    el_party_sums = mdb.get_object("election_party_sums")

    timeseries = el_party_sums[party]

    timeseries = {int(y): val/el_totals[y] for y,val in timeseries.items()}

    all_years = tuple(sorted(ELECTION_DATES.keys()))
    next_election_year = {this: next_ for (this, next_) in zip(all_years[0:-1], all_years[1:])}

    def get_election_dict(year):
        return dict(
            start=ELECTION_DATES[year],
            end=ELECTION_DATES[next_election_year[year]],
            value=timeseries[year])

    return [get_election_dict(y) for y in sorted(timeseries.keys())]


@cache.memoize(3600*24*30)
def party_leader_history(party_abbr):
    appointments = (db.session.query(GroupAppointment, Member.first_name, Member.last_name)
        .join(Member)
        .join(Group)
        .filter(GroupAppointment.role == 'Partiledare')
        .filter(Group.abbr == party_abbr)
        .order_by(GroupAppointment.start_date))

    results = []
    for app in appointments:
        results.append(dict(
            start=app.GroupAppointment.start_date,
            end=app.GroupAppointment.end_date,
            name='{} {}'.format(app.first_name, app.last_name)))

    return results



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

@cache.memoize(3600*24*30)
def get_best_party_time(abbr):
    data = mdb.get_object("best_party_time")

    party_data = data[abbr.lower()]
    out_data = []
    for key in sorted(party_data.keys()):
        year, month = map(int, key.split('M'))
        out_data.append(dict(time=dt.datetime(year, month, 1), value=party_data[key]))

    return out_data
