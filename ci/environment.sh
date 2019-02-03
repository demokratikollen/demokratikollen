export POSTGRES_DATA_HASH=$(md5sum demokratikollen/data/dumps/postgresql.tar.gz | cut -f1 -d' ')
export MONGO_DATA_HASH=$(md5sum demokratikollen/data/dumps/mongodb.tar.gz | cut -f1 -d' ')