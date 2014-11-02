START=$(date +%s.%N)
python import_data.py download data/urls.txt dl_data/
python import_data.py unpack dl_data/ dl_data/ --remove
python import_data.py clean dl_data/ dl_data/ --remove
python import_data.py wipe
python import_data.py execute dl_data/
python populate_orm.py
python compute_party_votes.py
END=$(date +%s.%N)
echo "Time elapsed:"
echo "$END - $START" | bc
