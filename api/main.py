from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from db.models import Protein, BindingSite, Gene
from db.database import SQLALCHEMY_DATABASE_URL, SessionLocal

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
   #range search - use query(x).filter(x.id.in_([1,3]))
   req_id = request.args.get('id', type=int)
   req_min = request.args.get('min', type=int)
   req_max = request.args.get('max', type=int)
   req_score_min = request.args.get('score_min', type=float)
   req_score_max = request.args.get('score_max', type=float)

   if(req_id==None and req_min==None and req_max == None and req_score_min == None and req_score_max == None):
      return "Supply arguments pls"

   filters = []
   if(req_id!=None):
      filters.append(BindingSiteModel.id == req_id)

   if(req_min!=None):
      filters.append(BindingSiteModel.start >= req_min)

   if(req_max != None):
      filters.append(BindingSiteModel.end <= req_max)

   if(req_score_min != None):
      filters.append(BindingSiteModel.score >= req_score_min)

   if(req_score_max != None):
      filters.append(BindingSiteModel.score <= req_score_max)


   result = BindingSiteModel.query.filter(*filters)
   return jsonify([log.serialize() for log in result])

@app.route('/genes')
def genes():
   req_symbol = request.args.get('symbol', type=str)
   req_id = request.args.get('id', type=str)

   if(req_symbol == None and req_id == None):
      return "<h1>Missing arguments<h1>"

   filters = []
   if(req_symbol != None):
      symbol_filter = GeneModel.symbol == req_symbol
      filters.append(symbol_filter)

   if(req_id != None):
      id_filter = GeneModel.id == req_id
      filters.append(id_filter)

   result = GeneModel.query.filter(*filters)
   return jsonify([log.serialize() for log in result])

@app.route('/proteins')
def proteins():
   req_name = request.args.get('protein_name', type=str)
   req_id = request.args.get('protein_id', type=str)
   
   if(req_name == None and req_id == None):
      return 'specify arguments plz'

   filters=[]
   if(req_name != None):
      filters.append(ProteinModel.protein_name == req_name)
   if(req_id != None):
      filters.append(ProteinModel.protein_id == req_id)

   result = ProteinModel.query.filter(*filters)
   return jsonify([log.serialize() for log in result])

@app.route('/join')
#binding sites - protein
def join():
   #TODO guide on sessions https://docs.sqlalchemy.org/en/13/orm/session_basics.html
   session = SessionLocal()

   query = []
   try:
      req_name = request.args.get('protein_name', type=str)
      #TODO this doesnt use indexes? use join?
      query = session.query(ProteinModel, BindingSiteModel).filter(ProteinModel.protein_name == req_name).all()
   except:
      session.rollback()
      raise
   finally:
      session.close()
   
   #TODO remoove 20 llimit and resolve too big requests somehow
   return jsonify([{**log.ProteinModel.serialize(), **log.BindingSiteModel.serialize()} for log in query][0:20])


if __name__ == '__main__':
   app.run()