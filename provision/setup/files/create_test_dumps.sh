#!/bin/bash

mkdir -p /home/vagrant/demokratikollen/data/dumps
rm -rf /home/vagrant/demokratikollen/data/dumps/postgres_dump.sql.gz
rm -rf /home/vagrant/demokratikollen/data/dumps/mongodb_dump.tar.gz
cd /home/vagrant/demokratikollen/data/dumps
pg_dump --no-owner demokratikollen | gzip > /home/vagrant/demokratikollen/data/dumps/postgres_dump.sql.gz
mongodump -o /home/vagrant/demokratikollen/data/dumps/mongodb_dump
tar -cvzf mongodb_dump.tar.gz mongodb_dump
rm -rf /home/vagrant/demokratikollen/data/dumps/mongodb_dump