import pandas as pd
from db.database import engine
from pathlib import PurePosixPath, Path


def import_proteins():
    # open file
    base_path = Path(__file__).parent
    csv_file_path = base_path / 'dummy_protein_df.csv'
    data_df = pd.read_csv(csv_file_path)

    # import to sql
    data_df.to_sql('proteins', index = False, con=engine, if_exists='append')


def import_binding_sites():
    # open file
    base_path = Path(__file__).parent
    csv_file_path = base_path / 'dummy_binding_sites_df.csv'
    data_df = pd.read_csv(csv_file_path)
    
    # import to sql
    data_df.to_sql('binding_sites', index = False, con=engine, if_exists='append')


def import_genes():
    # open file
    base_path = Path(__file__).parent
    csv_file_path = base_path / 'human_genes_ensrelease99.csv'
    data_df = pd.read_csv(csv_file_path)
    
    # import to sql
    data_df.to_sql('genes', index = False, con=engine, if_exists='append')