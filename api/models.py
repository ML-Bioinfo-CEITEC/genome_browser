from db.models import Protein, BindingSite, Gene, Prejoin
from db.database import db

#SQLAlchemy models converted to Flask-sqlalchemy models TODO: unite models? we need the query atribute https://docs.sqlalchemy.org/en/13/orm/query.html
class ProteinModel(db.Model, Protein):
   def serialize(self):
      return {
         'protein_name':self.protein_name,
         'protein_id':self.protein_id,
         'uniport_url':self.uniprot_url
      }
class BindingSiteModel(db.Model, BindingSite):
   def serialize(self):
      return {
         'id':self.id,
         'protein_name':self.protein_name,
         'chr':self.chr,
         'start':self.start,
         'end':self.end,
         'strand':self.strand,
         'score':self.score,
         'note':self.note
      }
class GeneModel(db.Model, Gene):
   def serialize(self):
      return {
         "id": self.id,
         "symbol": self.symbol,
         "biotype": self.biotype,
         "chr": self.chr,
         "start":self.start,
         "end":self.end,
         "strand":self.strand
      }

class PrejoinModel(db.Model, Prejoin):
   #TODO remove gene start and end, it's there just for our check
   def serialize(self):
      return {
         'id':self.bs_id,
         'protein_name':self.protein_name,
         'chr':self.chr,
         'start':self.bs_start,
         'end':self.bs_end,
         'strand':self.strand,
         'score':self.score,
         # 'gene_start':self.gene_start,
         # 'gene_end':self.gene_end,
         'symbol':self.symbol,
         'note':self.note,
      }
