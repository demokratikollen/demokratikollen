#!/bin/bash
echo "******CREATING RIKSDAGEN DATABASE******"
gosu postgres postgres --single <<- EOSQL
   CREATE DATABASE riksdagen;
   CREATE USER demokratikollen;
   GRANT ALL PRIVILEGES ON DATABASE riksdagen to demokratikollen;
EOSQL
echo ""
echo "******RIKSDAGEN DATABASE CREATED******"

echo "******CREATING DEMOKRATIKOLLEN DATABASE******"
gosu postgres postgres --single <<- EOSQL
   CREATE DATABASE demokratikollen;
   GRANT ALL PRIVILEGES ON DATABASE demokratikollen to demokratikollen;
EOSQL
echo ""
echo "******DOCKER DATABASE CREATED******"