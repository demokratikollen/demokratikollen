from db_structure import *
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.sql.expression import literal
from itertools import combinations
from demokratikollen.core.utils import PostgresUtils
import datetime as dt
import codecs

def compute_intervals(s, chair):

    one_day = dt.timedelta(days=1)

    q = s.query(ChamberAppointment) \
        .filter(ChamberAppointment.chair==chair)\
        .filter(ChamberAppointment.status != 'Ledig')\
        .order_by(ChamberAppointment.end_date.desc()).all()

    # fix dates to mean 'left side' of day
    starts = [(1,a,a.start_date) for a in q]
    ends = [(-1,a,a.end_date + one_day) for a in q]
    all_dates = starts+ends
    all_dates.sort(key=lambda t:t[2])


    out_intervals = []
    current_members = []
    last_date = dt.date(1900,1,1)

    for (delta, app, date) in all_dates:
        
        if delta == 1:
            if date != last_date:
                out_intervals.append( (last_date, date - one_day, list(current_members)) )
            current_members.append(app.id)
        else:
            if date != last_date:
                out_intervals.append( (last_date, date - one_day, list(current_members)) )
            current_members.remove(app.id)

        last_date = date

    return out_intervals

def main():

    engine = create_engine(PostgresUtils.engine_url())

    session = sessionmaker(bind=engine)
    s = session()
    one_day = dt.timedelta(days=1)

    f_trivial = codecs.open('chamber_consistency_trivial_overlaps.txt','w', encoding='utf-8')
    f_bad = codecs.open('chamber_consistency_bad_overlaps.txt','w', encoding='utf-8')
    f_empty_slots = codecs.open('chamber_consistency_empty_slots.txt','w', encoding='utf-8')

    appointments = {app.id: app for app in s.query(ChamberAppointment)}

    for chair in range(1,350):

        out_intervals = compute_intervals(s, chair)

        for i in out_intervals[1:]:
            if len(i[2]) == 0:
                f_empty_slots.write('Chair #{}: {} - {}\n'.format(chair, i[0],i[1]))
            if len(i[2]) > 1:
                overlap_msg = 'Chair #{}: {} - {}: {}\n'.format(chair,i[0],i[1], list(map(lambda x:appointments[x].title(),i[2])) )
                if i[1]-i[0] >= one_day:
                    f_bad.write(overlap_msg)
                else:
                    f_trivial.write(overlap_msg)

if __name__ == '__main__':
    main()

