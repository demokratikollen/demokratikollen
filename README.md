demokratikollen
===============

## Installation of PostgreSQL with python connection

- Download and install PostgreSQL: http://www.enterprisedb.com/postgresql-9351-installers-win64?ls=Crossover&type=Crossover
- Download and install python package `psycopg2` from Gohlke: http://www.lfd.uci.edu/~gohlke/pythonlibs/
- Install SqlAlchemy, eg. ``pip install sqlalchemy``

In PG, 
	1) set user 'postgres' password to "demokrati"
	2) create database "demokratikollen"

## Dependencies in Ubuntu (for development)

- PostgreSQL `sudo apt-get install postgresql postgresql-contrib` and developer's tools `sudo apt-get install posgresql-server-dev-all`
- Python dev tools `sudo apt-get install python-dev`
