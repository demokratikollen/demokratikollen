# -*- coding: utf-8 -*-
import db_structure
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Connection to postgres source
# import psycopg2
# conn_string = "host='localhost' dbname='riksdagen' user='postgres' password='demokrati'"
# conn = pg.connect(conn_string)

# Connection to mysql source
import mysql.connector
source_conn = mysql.connector.connect(user='root', password='demokrati',
                              host='localhost',
                              database='riksdagen')

# Connect to SQLAlchemy db and create structure
engine = create_engine('postgresql+psycopg2://postgres:demokrati@localhost:5432/demokratikollen')
db_structure.create_db_structure(engine)

session = sessionmaker()
session.configure(bind=engine)
s = session()

apa = Member(name='Arne Apa')
bepa = Poll(name='Bepavotering')
yes = VoteOption(name="yes")
bepa_yes = Vote(member=apa,poll=bepa,vote_option=yes)
kam = Unit(name='kam')
start = datetime.datetime.strptime('2010-01-01', '%Y-%m-%d').date()
end = datetime.datetime.strptime('2011-12-12', '%Y-%m-%d').date()
uppdrag = Assignment(unit=kam,member=apa,start_date=start,end_date=end)

s.add(apa)
s.add(bepa)
s.add(yes)
s.add(bepa_yes)
s.add(kam)
s.add(uppdrag)

s.commit()

c = source_conn.cursor()
c.execute("SELECT COUNT(DISTINCT intressent_id) FROM person;")
num_pers = c.fetchone()[0]
c.execute("SELECT COUNT(DISTINCT votering_id) FROM votering;")
num_votes = c.fetchone()[0]
print "Databasen innehåller {} ledamöter och {} voteringar.".format(num_pers,num_votes)

source_conn.close()
