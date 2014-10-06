from db_structure import *
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.sql.expression import literal
from itertools import combinations
import utils

import datetime as dt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
fig, axes = plt.subplots(1,1, figsize=(29/2.5, 20/2.5))


ax = axes

ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')

#engine = create_engine(utils.engine_url())

#session = sessionmaker(bind=engine)
#s = session()

#for x in s.query(ChamberAppointment).filter(ChamberAppointment.chair==1).all():
#	print(x)
start_date = dt.date(2014,5,29)
end_date = dt.date(2014,10,6)
#

ax.axvspan(start_date,end_date,0.1,0.2,fc='#ff00ff',ec='#0000ff',lw=1)
ax.set_xlim(dt.date(2010,9,1),dt.date(2014,9,1))
fig.autofmt_xdate()
fig.savefig('check_chamber_consistency.png',dpi=72)
plt.show()
