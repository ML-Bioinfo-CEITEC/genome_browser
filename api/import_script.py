from db.import_data_utils import prepare_binding_sites, prepare_genes, prepare_proteins, create_prejoin, delete_all_rows, analyze
from sqlalchemy import create_engine
from db.config import SQLALCHEMY_DATABASE_URL_PUBLIC

engine = create_engine(
    SQLALCHEMY_DATABASE_URL_PUBLIC, 
    echo=False, 
)
# only for db init
# create_all_tables()

#TODO check after dataset change, probably not needed, stats are there already (SELECT * from pg_stats;)
# analyze(engine)

#Create prejoin
create_prejoin(engine)
#TODO delete genes and binding sites to free up space?

#delete csv files from buckets