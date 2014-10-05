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

for chair in [1]:
	q = s.query(ChamberAppointment).filter(ChamberAppointment.chair==1).order_by(ChamberAppointment.end_date)
	for x in q.all():
		print(x)
