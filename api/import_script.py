from db.import_data_utils import prepare_binding_sites, prepare_genes, prepare_proteins, create_prejoin, delete_all_rows
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

#create csv_files folder and put all 3 csv files into it

#Adjust csv files
prepare_binding_sites("dummy_binding_sites_df.csv")
prepare_genes("human_genes_ensrelease99.csv")
prepare_proteins("dummy_protein_df.csv")

#Delete all records from all tables
# delete_all_rows(engine)

#Upload to buckets
#Insert from buckets to db tables

#Create prejoin
# create_prejoin(engine)
#TODO delete genes and binding sites to free up space?

#delete csv files from buckets