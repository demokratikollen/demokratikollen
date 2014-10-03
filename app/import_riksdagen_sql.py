# -*- coding: utf-8 -*-
import utils
import glob
import psycopg2
import os

def drop_all_riksdagen(conn):
    cur = conn.cursor()
    cur.execute("SELECT table_schema,table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_schema,table_name")
    rows = cur.fetchall()
    for row in rows:
        print("Dropping table {}".format(row[1]))
        cur.execute("drop table {} cascade".format(row[1]))
    cur.close()

with psycopg2.connect(os.environ['DATABASE_RIKSDAGEN_URL']) as conn:

    # Create database
    if utils.yes_or_no("Do you want to drop all tables and recreate the Riksdagen database?"):
        drop_all_riksdagen(conn)
        print("Creating tables in database")
        utils.run_sql('riksdagen_sql/create_tables.sql',conn)

    # for i,sql_file in enumerate(glob.glob('/vagrant/data/*.sql')):
    #     print("Running '{}'".format(sql_file))
    #     utils.run_sql(sql_file,conn)