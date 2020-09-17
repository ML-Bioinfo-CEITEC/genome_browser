import pandas as pd
from db.database import engine, db
from pathlib import PurePosixPath, Path
from db.models import Prejoin, Gene, BindingSite
from models import PrejoinModel, BindingSiteModel, GeneModel
from sqlalchemy import orm


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

def import_to_prejoin():
    # TODO am i creating the session correctly?
    session = orm.scoped_session(orm.sessionmaker())(bind=engine)

    query = session.query(BindingSiteModel, GeneModel)
    #TODO >= vs >
    query = query.join(GeneModel, (GeneModel.strand == BindingSiteModel.strand) & (GeneModel.chr == BindingSiteModel.chr) & (BindingSiteModel.end > GeneModel.start) & (BindingSiteModel.start < GeneModel.end))
    results = query.all()

    def get_row_from_res(result):
        bs = result.BindingSiteModel
        g = result.GeneModel
        row = Prejoin(bs.id, bs.protein_name, bs.chr, bs.start, bs.end, bs.strand, bs.score, bs.note, g.id, g.symbol, g.start, g.end)
        return row

    rows = [get_row_from_res(res) for res in results]
    for row in rows:
        session.add(row)
    session.commit()

def analyze():
    with engine.connect() as con:
        con.execute('ANALYZE;')

def cleanup():
    Gene.__table__.drop(engine)
    BindingSite.__table__.drop(engine)





