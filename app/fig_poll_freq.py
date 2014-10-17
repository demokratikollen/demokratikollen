from db_structure import *
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.sql.expression import literal
from itertools import combinations
from utils import PostgresUtils, MiscUtils,MongoDBDatastore
import datetime as dt
import codecs
import json
from flask.json import jsonify



def poll_freq():

    engine = create_engine(PostgresUtils.engine_url())
    session = sessionmaker(bind=engine)
    s = session()



    weekday = {k: 0 for k in range(1,8)}
    month = {k: 0 for k in range(1,13)}
    day = {k: 0 for k in range(1,32)}
    exact = dict()

    for poll in s.query(Poll).all():
        weekday[poll.date.isoweekday()] += 1
        month[poll.date.month] += 1
        day[poll.date.day] += 1

        timestamp = dt.datetime.combine(poll.date,dt.time(0)).timestamp()
        if timestamp in exact:
            exact[timestamp] += 1
        else:
            exact[timestamp] = 1


    datastore = MongoDBDatastore() 
    datastore.store_string(json.dumps(weekday),'poll_frequency_weekday')
    datastore.store_string(json.dumps(month),'poll_frequency_month')
    datastore.store_string(json.dumps(day),'poll_frequency_day')
    datastore.store_string(json.dumps(exact),'poll_frequency_exact')

def main():
    poll_freq()

if __name__ == '__main__':
    main()