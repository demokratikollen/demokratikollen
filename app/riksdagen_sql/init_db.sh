#/bin/sh

psql -U vagrant -d riksdagen -q -f create_tables.sql
psql -U vagrant -d riksdagen -q -f psql_person.sql