START=$(date +%s.%N)
python populate_orm.py
python compute_party_votes.py
python calculations/party_covoting.py
python calculations/sankey_data.py
python calculations/election_data.py
python calculations/cosigning.py
python calculations/search.py
python calculations/scb_best_party_education.py
python calculations/scb_best_party_gender.py
python calculations/scb_best_party_time.py
END=$(date +%s.%N)
echo "Time elapsed:"
echo "$END - $START" | bc
