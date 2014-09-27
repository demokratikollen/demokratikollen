# -*- coding: utf-8 -*-

# Connection to postgres
# import psycopg2
# conn_string = "host='localhost' dbname='riksdagen' user='postgres' password='demokrati'"
# conn = pg.connect(conn_string)

# Connection to mysql
import mysql.connector
conn = mysql.connector.connect(user='root', password='demokrati',
                              host='localhost',
                              database='riksdagen')

c = conn.cursor()
c.execute("SELECT COUNT(DISTINCT intressent_id) FROM person;")
num_pers = c.fetchone()[0]
c.execute("SELECT COUNT(DISTINCT votering_id) FROM votering;")
num_votes = c.fetchone()[0]
print "Databasen innehåller {} ledamöter och {} voteringar.".format(num_pers,num_votes)

conn.close()
