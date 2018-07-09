#!/usr/bin/env bash
set -e


START=$(date +%s.%N)
python import_data.py download data/urls.txt dl_data/
python import_data.py unpack dl_data/ dl_data/ --remove
python import_data.py clean dl_data/ dl_data/ --remove
python import_data.py wipe
python import_data.py execute dl_data/
python populate_orm.py
python compute_party_votes.py
python calculations/party_covoting.py
python calculations/sankey_data.py
python calculations/election_data.py
python calculations/cosigning.py
python calculations/search.py
python calculations/scb_best_party_gender.py
python calculations/scb_best_party_education.py
python calculations/scb_elections.py
python calculations/scb_polls.py
END=$(date +%s.%N)
echo "Time elapsed:"
echo "$END - $START" | bc
