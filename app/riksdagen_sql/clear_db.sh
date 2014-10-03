#/bin/sh

psql -U vagrant -d riksdagen -t -c "select 'drop table \"' || tablename || '\" cascade;' from pg_tables where schemaname = 'public'" | psql -U vagrant -d riksdagen