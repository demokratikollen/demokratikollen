#/bin/sh

psql -U vagrant -d riksdagen -q -f create_tables.sql
psql -U vagrant -d riksdagen -q -f psql_person.sql
psql -U vagrant -d riksdagen -q -f psql_votering-201314.sql