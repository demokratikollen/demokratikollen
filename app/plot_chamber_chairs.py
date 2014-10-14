from db_structure import *
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.sql.expression import literal, distinct
from itertools import combinations
from utils import PostgresUtils
import datetime as dt
import codecs
import numpy as np
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from collections import OrderedDict
import os

def main():
    
    fig_dir = 'chamber_chair_figs'

    if not os.path.exists(fig_dir):
        os.makedirs(fig_dir)

    engine = create_engine(PostgresUtils.engine_url()) 
    session = sessionmaker(bind=engine)
    s = session()


    for chair in range(1,350):
        q = s.query(ChamberAppointment).join(Member) \
            .filter(ChamberAppointment.chair==chair) \
            .order_by(ChamberAppointment.end_date.desc())
        
     
     
        rows = OrderedDict()
        for app in q:
            if not app.member.id in rows:
                rows[app.member.id] = [app]
            else:
                rows[app.member.id].append(app)


        hatches = {'Tjänstgörande':'','Ledig':'x'}
        colors = {'Riksdagsledamot': '#ff0000', 'Ersättare':'#aaaa22'}


        fig = plt.figure(0,figsize=(100,len(rows)))
        ax = fig.add_subplot(111)    

        y = 0
        yticklabelss = []
        yticks = []
        for (member_id, apps) in rows.items():

            member = s.query(Member).filter(Member.id == member_id).one()

            yticks.append(y+0.5)
            yticklabelss.append(repr(member))

            for app in apps:
                ax.barh(y,mdates.date2num(app.end_date)-mdates.date2num(app.start_date),left=app.start_date,
                    hatch=hatches[app.status],
                    color=colors[app.role],
                    linewidth=0)

            y += 1


        ax.set_yticks(yticks)
        ax.set_yticklabels(yticklabelss)
        ax.xaxis_date()
        plt.tight_layout()

        fig.savefig('{}/{:03d}.png'.format(fig_dir,chair))
        
        plt.clf()
if __name__ == '__main__':
        main()  