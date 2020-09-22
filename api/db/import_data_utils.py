import pandas as pd
from pathlib import PurePosixPath, Path
from sqlalchemy import orm

from db.database import engine, db
from models import PrejoinModel, BindingSiteModel, GeneModel
from db.models import Prejoin, Gene, BindingSite, Protein
import db.models



base_path = Path(__file__).parent/"csv_files"
def import_proteins():
    # open file
    folder_path = base_path /"proteins"
    csv_file_path = list(folder_path.iterdir())[0]
    data_df = pd.read_csv(csv_file_path)

    # import to sql
    data_df.to_sql('proteins', index = False, con=engine, if_exists='append')



def import_binding_sites():
    # open file
    folder_path = base_path /"binding_sites"
    csv_file_path = list(folder_path.iterdir())[0]
    data_df = pd.read_csv(csv_file_path)
    
    # import to sql
    data_df.to_sql('binding_sites', index = False, con=engine, if_exists='append')


def import_genes():
    # open file
    folder_path = base_path /"genes"
    csv_file_path = list(folder_path.iterdir())[0]
    data_df = pd.read_csv(csv_file_path)
    
    # import to sql
    data_df.to_sql('genes', index = False, con=engine, if_exists='append')

def import_to_prejoin_no_ram():
    session = orm.scoped_session(orm.sessionmaker())(bind=engine)

    sql = "INSERT INTO prejoin SELECT binding_sites.id AS bs_id, binding_sites.protein_name AS protein_name, binding_sites.chr AS chr, binding_sites.start AS bs_start, binding_sites.end AS bs_end, binding_sites.strand AS strand, binding_sites.score AS score, binding_sites.note AS note, genes.id AS gene_id, genes.symbol AS symbol, genes.start AS gene_start, genes.end AS gene_end FROM binding_sites JOIN genes ON genes.strand = binding_sites.strand AND genes.chr = binding_sites.chr AND binding_sites.end > genes.start AND binding_sites.start < genes.end"
    try:
        session.execute(sql)
        session.commit()
    except:
        session.rollback()
    finally:
        session.close()

def import_to_prejoin():
    session = orm.scoped_session(orm.sessionmaker())(bind=engine)

    query = session.query(BindingSiteModel, GeneModel)
    #TODO >= vs >
    query = query.join(GeneModel, (GeneModel.strand == BindingSiteModel.strand) & (GeneModel.chr == BindingSiteModel.chr) & (BindingSiteModel.end > GeneModel.start) & (BindingSiteModel.start < GeneModel.end))
    
    def get_row_from_res(result):
            bs = result.BindingSiteModel
            g = result.GeneModel
            row = Prejoin(bs.id, bs.protein_name, bs.chr, bs.start, bs.end, bs.strand, bs.score, bs.note, g.id, g.symbol, g.start, g.end)
            return row
    try:
        results = query.all()
        rows = [get_row_from_res(res) for res in results]
        for row in rows:
            session.add(row)
        session.commit()
    except:
        session.rollback()
    finally:
        session.close()

def analyze():
    with engine.connect() as con:
        con.execute('ANALYZE;')

def cleanup():
    Gene.__table__.drop(engine)
    BindingSite.__table__.drop(engine)


def recreate_all_tables():
    Prejoin.__table__.drop(engine)
    Protein.__table__.drop(engine)
    db.models.Base.metadata.create_all(bind=db.models.engine)

def create_all_tables():
    db.models.Base.metadata.create_all(bind=db.models.engine)


def generate_ids_for_bs():
    folder_path = base_path /"binding_sites"
    csv_file_path = list(folder_path.iterdir())[0]
    data_df = pd.read_csv(csv_file_path)
    data_df.to_csv(folder_path/'bs_with_ids_no_header.csv', index_label="id", index=True, header=False)

#TODO loads the whole thing to ram 
def decapitate_proteins():
    # open file
    folder_path = base_path /"proteins"
    csv_file_path = list(folder_path.iterdir())[0]
    data_df = pd.read_csv(csv_file_path)
    data_df.to_csv(folder_path/'proteins_no_header.csv', header=False, index=False)


def decapitate_genes():
    # open file
    folder_path = base_path /"genes"
    csv_file_path = list(folder_path.iterdir())[0]
    data_df = pd.read_csv(csv_file_path)
    data_df.to_csv(folder_path/'genes_no_header.csv', header=False, index=False)

    





