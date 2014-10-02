# -*- coding: utf-8 -*-
import sqlite3
import os

def run_sql(db_file,sql_file):
    qry = open(sql_file, 'r').read()
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.executescript(qry)
    conn.commit()
    c.close()
    conn.close()

if __name__ == '__main__':
    data_dir = 'D:/data/demokratikollen/Import från Riksdagen/'
    db_file = os.path.join(data_dir,'riksdagen.db')
    # sql_file = os.path.join(data_dir,'create_tables.sql')
    # sql_file = os.path.join(data_dir,'votering-201011.sql')
    sql_file = os.path.join(data_dir,'person.sql')

    run_sql(db_file,sql_file)