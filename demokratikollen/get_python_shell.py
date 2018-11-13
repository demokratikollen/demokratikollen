import os

import psycopg2 as pg
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker
from demokratikollen.core.utils import postgres as pg_utils
from demokratikollen.core.db_structure import *


# pgsql
source_conn = pg.connect(os.environ['DATABASE_RIKSDAGEN_URL'])
c = source_conn.cursor()


# Connect to SQLAlchemy db and create structure
engine = create_engine(pg_utils.engine_url())
session = sessionmaker()
session.configure(bind=engine)
s = session()

import IPython; IPython.embed()