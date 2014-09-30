demokratikollen
===============

## Installation of development dependencies (Ubuntu)

Assumes you have cloned the repository.

1. Install PostgreSQL: `sudo apt-get install postgresql postgresql-contrib posgresql-server-dev-all`
2. Set password and create database
  1. Get into `psql` console as user `postgres`: `sudo -u postgres psql postgres`
  2. Change password: `\password postgres` and set to `demokrati`
  3. Exit console with Ctrl-D (or `\q`)
  4. Create database: `sudo -u postgres createdb demokratikollen`
3. Install `pip` and python dev-tools: `sudo apt-get install python-dev python-pip`
4. Set up and activate virtual environment
  1. Install `virtualenv`: `pip install virtualenv`
  2. Create virtual environment: `virtualenv path/to/demokratikollen/`
  3. Activate (to use local binaries): `cd path/to/demokratikollen` => `source bin/activate`
  4. Install requirements: `pip install -r requirements.txt` 

## Installation of PostgreSQL with python connection (Windows)

- Download and install PostgreSQL: http://www.enterprisedb.com/postgresql-9351-installers-win64?ls=Crossover&type=Crossover
- Download and install python package `psycopg2` from Gohlke: http://www.lfd.uci.edu/~gohlke/pythonlibs/
- Install SqlAlchemy, eg. ``pip install sqlalchemy``

In PG, 
	1) set user 'postgres' password to "demokrati"
	2) create database "demokratikollen"
