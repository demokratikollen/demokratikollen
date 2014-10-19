from demokratikollen.core.db_structure import *
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.sql.expression import literal, distinct
from itertools import combinations
from demokratikollen.core.utils import PostgresUtils
import datetime as dt
import codecs
import numpy as np
import matplotlib
matplotlib.use('Agg')
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from collections import OrderedDict
import os

from check_chamber_consistency import compute_intervals

def main():
    
    fig_dir = 'chamber_chair_figs'

    if not os.path.exists(fig_dir):
        os.makedirs(fig_dir)

    engine = create_engine(PostgresUtils.engine_url()) 
    session = sessionmaker(bind=engine)
    s = session()
    one_day = dt.timedelta(days=1)


    for chair in range(1,350):

        out_intervals = compute_intervals(s, chair)

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
        yticklabels = []
        yticks = []
        for (member_id, apps) in rows.items():

            member = s.query(Member).filter(Member.id == member_id).one()

            yticks.append(y+0.5)
            yticklabels.append(repr(member))

            for app in apps:
                ax.barh(y,mdates.date2num(app.end_date+one_day)-mdates.date2num(app.start_date),
                    height=1.0,
                    left=app.start_date,
                    hatch=hatches[app.status],
                    color=colors[app.role],
                    linewidth=0)

            y += 1

        for i in out_intervals[1:]:
            if len(i[2]) == 0: #empty chair
                if i[1]-i[0] >= one_day:
                    ax.axvspan(i[0],i[1]+one_day, facecolor='#0000ff', alpha=0.5, linewidth=0)
                    ax.text(i[1]+one_day, y, 'Empty {}-{}'.format(i[0],i[1]),rotation=0)
                else:
                    ax.axvspan(i[0],i[1]+one_day, facecolor='#00ffff', alpha=0.5, linewidth=0)
                    ax.text(i[1]+one_day, y, 'Empty one day {}'.format(i[0]),rotation=0)


            if len(i[2]) > 1:
                if i[1]-i[0] >= one_day:
                    ax.axvspan(i[0],i[1]+one_day, facecolor='#ff0000', alpha=0.5, linewidth=0)
                    ax.text(i[1]+one_day, y, 'n={}: Overlap {}-{}'.format(len(i[2]),i[0],i[1]),rotation=0)

                else:
                    ax.axvspan(i[0],i[1]+one_day, facecolor='#ffff00', alpha=0.5, linewidth=0)
                    ax.text(i[1]+one_day, y, 'n={}: One day overlap {}'.format(len(i[2]),i[0]),rotation=0)

        ax.set_ylim(0,y+1)
        ax.yaxis.grid()
        ax.set_yticks(yticks)
        ax.set_yticklabels(yticklabels)

        ax.xaxis_date()
        ax.set_xlim(ax.get_xlim()[0],date(2019,1,1))


        years    = mdates.YearLocator()   # every year
        months   = mdates.MonthLocator()  # every month
        yearsFmt = mdates.DateFormatter('%Y')        
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(yearsFmt)
        ax.xaxis.set_minor_locator(months)

        fig.autofmt_xdate()
        plt.tight_layout()

        fig.savefig('{}/{:03d}.pdf'.format(fig_dir,chair))
        
        plt.clf()
if __name__ == '__main__':
        main()  