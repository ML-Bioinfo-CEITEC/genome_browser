from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from db.models import Protein, BindingSite, Gene
from db.database import SQLALCHEMY_DATABASE_URL

app = Flask(__name__)
#TODO URI vs URL
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URL
db = SQLAlchemy(app)
#TODO migrations?

#TODO move models and db to separate files
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


@app.route('/bindings')
def bindings():
   req_id = request.args.get('id', default="", type=int)
   result = BindingSiteModel.query.filter(BindingSiteModel.id == req_id)
   return jsonify([log.serialize() for log in result])

@app.route('/genes')
def genes():
   req_symbol = request.args.get('symbol', default="", type=str)
   result = GeneModel.query.filter(GeneModel.symbol == req_symbol)
   return jsonify([log.serialize() for log in result])

@app.route('/proteins')
def protein_by_name():
   requested_name = request.args.get('protein_name', default="", type=str)
   result = ProteinModel.query.filter(ProteinModel.protein_name == requested_name)
   return jsonify([log.serialize() for log in result])

if __name__ == '__main__':
   app.run()