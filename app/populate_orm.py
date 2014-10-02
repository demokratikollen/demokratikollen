# -*- coding: utf-8 -*-
import db_structure
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import utils

# Connection to postgres source
# import psycopg2
# conn_string = "host='localhost' dbname='riksdagen' user='postgres' password='demokrati'"
# conn = pg.connect(conn_string)

# Connection to mysql source
# import mysql.connector
# source_conn = mysql.connector.connect(user='root', password='demokrati',
#                               host='localhost',
#                               database='riksdagen')

# Connect to SQLAlchemy db and create structure
engine = create_engine(utils.engine_url())
db_structure.create_db_structure(engine)

session = sessionmaker()
session.configure(bind=engine)
s = session()


c = source_conn.cursor()
c.execute("SELECT COUNT(DISTINCT intressent_id) FROM person;")
num_pers = c.fetchone()[0]
c.execute("SELECT COUNT(DISTINCT votering_id) FROM votering;")
num_votes = c.fetchone()[0]
print "Databasen innehåller {} ledamöter och {} voteringar.".format(num_pers,num_votes)

source_conn.close()
