import pandas as pd
from pathlib import PurePosixPath, Path
from sqlalchemy import orm

from db.database import engine, db
from models import PrejoinModel, BindingSiteModel, GeneModel
from db.models import Prejoin, Gene, BindingSite, Protein
import db.models

base_path = Path(__file__).parent/"csv_files"
def create_prejoin(engine):
    session = orm.scoped_session(orm.sessionmaker())(bind=engine)

    sql = "INSERT INTO prejoin SELECT binding_sites.id AS bs_id, binding_sites.protein_name AS protein_name, binding_sites.chr AS chr, binding_sites.start AS bs_start, binding_sites.end AS bs_end, binding_sites.strand AS strand, binding_sites.score AS score, binding_sites.note AS note, genes.id AS gene_id, genes.symbol AS symbol, genes.start AS gene_start, genes.end AS gene_end FROM binding_sites JOIN genes ON genes.strand = binding_sites.strand AND genes.chr = binding_sites.chr AND binding_sites.end >= genes.start AND binding_sites.start <= genes.end"
    try:
        session.execute(sql)
        session.commit()
        print("Table created OK")
    except  Exception as e:
        print(e)
        print("ROLLBACK")
        session.rollback()
    finally:
        session.close()

def delete_all_rows(engine):
    session = orm.scoped_session(orm.sessionmaker())(bind=engine)

    sql = "DELETE FROM prejoin; DELETE FROM binding_sites; DELETE FROM genes; DELETE FROM proteins;"
    try:
        session.execute(sql)
        session.commit()
        print("Deletion OK")
    except Exception as e:
        print(e)
        print("ROLLBACK")
        session.rollback()
    finally:
        session.close()

#TODO check after dataset change, probably not needed, stats are there already (SELECT * from pg_stats;)
def analyze(engine):
    with engine.connect() as con:
        con.execute('ANALYZE;')

def create_all_tables():
    db.models.Base.metadata.create_all(bind=db.models.engine)

def prepare_binding_sites(csv_name):
    csv_file_path = base_path/csv_name
    data_df = pd.read_csv(csv_file_path)
    data_df.to_csv(base_path/"prepared"/'binding_sites_prepared.csv', index_label="id", index=True, header=False)
    print("Binding sites csv preparation OK")

def prepare_proteins(csv_name):
    csv_file_path = base_path /csv_name
    data_df = pd.read_csv(csv_file_path)
    data_df.to_csv(base_path/"prepared"/'proteins_prepared.csv', header=False, index=False)
    print("Proteins csv preparation OK")

def prepare_genes(csv_name):
    csv_file_path = base_path /csv_name
    data_df = pd.read_csv(csv_file_path)
    data_df.to_csv(base_path/"prepared"/'genes_prepared.csv', header=False, index=False)
    print("Genes csv preparation OK")


    





