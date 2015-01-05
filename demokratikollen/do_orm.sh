START=$(date +%s.%N)
python populate_orm.py
python compute_party_votes.py
python calculations/party_covoting.py
python calculations/sankey_data.py
python calculations/election_data.py
python calculations/cosigning.py
END=$(date +%s.%N)
echo "Time elapsed:"
echo "$END - $START" | bc
