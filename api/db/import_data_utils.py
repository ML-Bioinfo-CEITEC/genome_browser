import pandas as pd
from db.database import engine, db
from pathlib import PurePosixPath, Path
from db.models import Prejoin, Gene, BindingSite, Protein
from models import PrejoinModel, BindingSiteModel, GeneModel
from sqlalchemy import orm
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

    





