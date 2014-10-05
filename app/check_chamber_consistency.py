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

errors = []
for chair in range(1,350):
	q = s.query(ChamberAppointment).filter(ChamberAppointment.chair==chair).order_by(ChamberAppointment.end_date.desc()).all()

	print ('Chair #{}'.format(chair))
	ok_until = q[0].start_date	
	for a in q[1:]:
		if a.status == "Ledig":
			continue
		if a.end_date == ok_until:
			ok_until = a.start_date
		elif a.end_date + dt.timedelta(days=1) == ok_until:
			ok_until = a.start_date
			print('WARNING: one day error at {}'.format(a.end_date))
		else:
			print('Break at {}, next app ends at {}'.format(ok_until,a.end_date))
			print (a)
			errors.append('Chair #{}: Break at {}, next app ends at {}'.format(chair,ok_until,a.end_date))
			break

		if ok_until < dt.date(2006,1,1):
			break

	print('Ok until {}'.format(ok_until))
for err in errors:
	print (err)