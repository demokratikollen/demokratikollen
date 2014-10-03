# -*- coding: utf-8 -*-
from sqlalchemy.engine import reflection
from sqlalchemy.schema import MetaData,Table,DropTable,ForeignKeyConstraint,DropConstraint
import sys
import psycopg2
import os


def drop_everything(engine):
    """Drop everything in database.
    Source: https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/DropEverything
    """
    conn = engine.connect()

    # the transaction only applies if the DB supports
    # transactional DDL, i.e. Postgresql, MS SQL Server
    trans = conn.begin()

    inspector = reflection.Inspector.from_engine(engine)

    # gather all data first before dropping anything.
    # some DBs lock after things have been dropped in
    # a transaction.
    metadata = MetaData()

    tbs = []
    all_fks = []

    for table_name in inspector.get_table_names():
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            if not fk['name']:
                continue
            fks.append(ForeignKeyConstraint((),(),name=fk['name']))
        t = Table(table_name,metadata,*fks)
        tbs.append(t)
        all_fks.extend(fks)

    for fkc in all_fks:
        conn.execute(DropConstraint(fkc))
    for table in tbs:
        conn.execute(DropTable(table))
    trans.commit()

def database_url():
    """returns database_url from env if it exists, otherwise default"""

    if 'DATABASE_URL' in os.environ:
        return os.environ['DATABASE_URL']
    else:
        return 'postgresql://postgres:demokrati@localhost:5432/demokratikollen'

def engine_url():
    """Returns the engine url taken from the database_url,
    probably needs something more robust sooner or later"""
    url_components = database_url().split("//")
    return 'postgresql+psycopg2://' + url_components[1]

def yes_or_no(question, default=True):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    Returns True or False
    Based on the recipe http://code.activestate.com/recipes/577058/
    """
    valid = {"yes":True,   "y":True,  "ye":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == True:
        prompt = " [Y/n] "
    elif default == False:
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return default
        elif choice in list(valid.keys()):
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")

def execute_sql(qry,conn):
    c = conn.cursor()
    c.execute(qry)
    c.close()
    conn.commit()

def run_sql(sql_file,conn):
    """Run SQL file in PostgreSQL."""
    with open(sql_file,mode='U') as f:
        qry = f.read()
    execute_sql(qry,conn)

