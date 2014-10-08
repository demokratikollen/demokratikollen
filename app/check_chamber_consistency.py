from db_structure import *
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.sql.expression import literal
from itertools import combinations
import utils
import datetime as dt
engine = create_engine(utils.engine_url())

session = sessionmaker(bind=engine)
s = session()

for chair in range(1,350):
	q = s.query(ChamberAppointment) \
		.filter(ChamberAppointment.chair==chair)\
		.filter(ChamberAppointment.status != 'Ledig')\
		.order_by(ChamberAppointment.end_date.desc()).all()

	starts = [(1,a,a.start_date) for a in q]
	ends = [(-1,a,a.end_date) for a in q]
	all_dates = starts+ends
	all_dates.sort(key=lambda t:t[2])


	one_day = dt.timedelta(days=1)
	out_intervals = []
	current_members = []
	last_date = dt.date(1900,1,1)

	for (delta, app, date) in all_dates:
		
		if delta == 1:
			if date != last_date:
				out_intervals.append( (last_date, date - one_day, current_members) )
			current_members.append(app.member.id)
		else:
			if date != last_date:
				out_intervals.append( (last_date, date, current_members) )
			current_members.remove(app.member.id)

		last_date = date

	print('Chair #{}'.format(chair))
	for i in out_intervals[1:]:
		if len(i[2]) == 0:
			print('{} - {}: Chair empty.'.format(i[0],i[1]))
		if len(i[2]) > 1:
			print('{} - {}: Multiple: {}'.format(i[0],i[1],i[2]))