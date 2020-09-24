from db.import_data_utils import prepare_binding_sites, prepare_genes, prepare_proteins, create_prejoin, delete_all_rows, analyze
from sqlalchemy import create_engine
from db.config import SQLALCHEMY_DATABASE_URL_PUBLIC

engine = create_engine(
    SQLALCHEMY_DATABASE_URL_PUBLIC, 
    echo=False, 
)

#Create prejoin table
create_prejoin(engine)
#TODO possible upgrade: delete genes and binding sites to free up space