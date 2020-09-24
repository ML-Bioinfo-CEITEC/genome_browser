from db.import_data_utils import prepare_binding_sites, prepare_genes, prepare_proteins
from sqlalchemy import create_engine
from db.config import SQLALCHEMY_DATABASE_URL_PUBLIC

engine = create_engine(
    SQLALCHEMY_DATABASE_URL_PUBLIC, 
    echo=False, 
)

### YOUR CSV FILE NAMES GO HERE ###
binding_sites_csv_name = "dummy_binding_sites_df.csv"
genes_csv_name = "human_genes_ensrelease99.csv"
proteins_csv_name = "dorina_clipseq_proteins_df.csv"

#Adjust csv files
prepare_binding_sites(binding_sites_csv_name)
prepare_genes(genes_csv_name)
prepare_proteins(proteins_csv_name)

#Delete all records from all tables
#TODO staging db so there is no downtime?
delete_all_rows(engine)

#Upload to buckets
#Insert from buckets to db tables
