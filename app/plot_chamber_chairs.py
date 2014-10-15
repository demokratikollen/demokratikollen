from db_structure import *
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.sql.expression import literal, distinct
from itertools import combinations
import utils
import datetime as dt
import codecs
import numpy as np
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_intervals(members, chair):


    for member in members:
        for app in (app for app in member.appointments if app.chair):
            print(app)


def main():
    

    engine = create_engine(utils.engine_url())

    session = sessionmaker(bind=engine)
    s = session()


    chair = 7
    sq = s.query(ChamberAppointment) \
        .filter(ChamberAppointment.chair==chair) \
        .order_by(ChamberAppointment.end_date.asc()).subquery()
    
    # distinct members which have been on this chair
    members = s.query(Member).filter(Member.id.in_( s.query(distinct(sq.c.member_id)) ))

    fig = plt.figure(figsize=(10,8))
    ax = fig.add_subplot(111)    
 
    y = 0
    for m in members: 
        apps = s.query(ChamberAppointment) \
                .filter(ChamberAppointment.chair==chair) \
                .filter(ChamberAppointment.member_id == m.id) \
                .order_by(ChamberAppointment.end_date.asc())
        for app in apps:

            ax.barh(y,mdates.date2num(app.end_date)-mdates.date2num(app.start_date),left=app.start_date)

        y += 1
    ax.xaxis_date()
    fig.savefig('test.png')

if __name__ == '__main__':
        main()  