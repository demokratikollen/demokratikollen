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

import numpy as np
import matplotlib
matplotlib.use('Agg')
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def poll_freq():

    engine = create_engine(PostgresUtils.engine_url())
    session = sessionmaker(bind=engine)
    s = session()




    weekday = {k: 0 for k in range(1,8)}
    week = {k: 0 for k in range(1,54)}
    month = {k: 0 for k in range(1,13)}
    day = {k: 0 for k in range(1,32)}
    exact = dict()

    for poll in s.query(Poll).all():
        weekday[poll.date.isoweekday()] += 1
        week[poll.date.isocalendar()[1]] += 1
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
    datastore.store_string(json.dumps(month),'poll_frequency_week')
    datastore.store_string(json.dumps(day),'poll_frequency_day')
    datastore.store_string(json.dumps(exact),'poll_frequency_exact')


    fig = plt.figure(0, figsize=(10,10))
    ax = fig.add_subplot(111)
    xs = np.arange(1,8)-0.4
    ax.bar(xs, [weekday[i] for i in range(1,8)])
    ax.set_xticks(np.arange(1,8))
    fig.savefig('pollfreq_weekday.png')
    plt.clf()

    fig = plt.figure(0, figsize=(10,10))
    ax = fig.add_subplot(111)
    xs = np.arange(1,13)-0.4
    ax.bar(xs, [month[i] for i in range(1,13)])
    ax.set_xticks(np.arange(1,13))
    fig.savefig('pollfreq_month.png')
    plt.clf()

    fig = plt.figure(0, figsize=(20,10))
    ax = fig.add_subplot(111)
    xs = np.arange(1,54)-0.4
    ax.bar(xs, [week[i] for i in range(1,54)])
    ax.set_xticks(np.arange(1,54,5))
    fig.savefig('pollfreq_week.png')
    plt.clf()

    fig = plt.figure(0, figsize=(10,10))
    ax = fig.add_subplot(111)
    xs = np.arange(1,32)-0.4
    ax.bar(xs, [day[i] for i in range(1,32)])
    ax.set_xticks(np.arange(1,32))
    fig.savefig('pollfreq_day.png')
    plt.clf()

def main():
    poll_freq()

if __name__ == '__main__':
    main()