import pandas as pd
from database import engine

base_path = 'C:/Users/Vlastimil Martinek/Documents/repos/projectBakery/api/db'

csv_file_path = f'{base_path}/dummy_protein_df.csv'
with open(csv_file_path, 'r') as file:
    data_df = pd.read_csv(file)
data_df.to_sql('proteins', index = False, con=engine, if_exists='append')

csv_file_path = f'{base_path}/dummy_binding_sites_df.csv'
with open(csv_file_path, 'r') as file:
    data_df = pd.read_csv(file)
data_df.to_sql('binding_sites', index = False, con=engine, if_exists='append')

csv_file_path = f'{base_path}/human_genes_ensrelease99.csv'
with open(csv_file_path, 'r') as file:
    data_df = pd.read_csv(file)
data_df.to_sql('genes', index = False, con=engine, if_exists='append')