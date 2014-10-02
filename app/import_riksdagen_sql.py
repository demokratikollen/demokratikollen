# -*- coding: utf-8 -*-
import utils
import glob

# Create database
# print "Creating tables in database"
# utils.run_sql('riksdagen_sql/create_tables.sql')

for sql_file in glob.glob('/vagrant/data/psql_person.sql'):
    print "Running '{}'".format(sql_file)
    utils.run_sql(sql_file)
    exit()

