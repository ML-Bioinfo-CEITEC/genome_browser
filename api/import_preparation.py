from db.import_data_utils import prepare_binding_sites, prepare_genes, prepare_proteins, delete_all_rows
from sqlalchemy import create_engine
from db.config import SQLALCHEMY_DATABASE_URL_LOCAL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL_LOCAL, 
    echo=False, 
)

### YOUR CSV FILE NAMES FROM api/db/csv_files GO HERE ###
binding_sites_csv_name = "dummy_binding_sites_df.csv"
genes_csv_name = "human_genes_ensrelease99.csv"
proteins_csv_name = "dorina_clipseq_proteins_df.csv"


#Adjust csv files
prepare_binding_sites(binding_sites_csv_name)
prepare_genes(genes_csv_name)
prepare_proteins(proteins_csv_name)

#Delete all records from all tables
#TODO possible upgrade: staging db so there is no downtime
delete_all_rows(engine)
