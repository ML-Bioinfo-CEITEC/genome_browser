from flask import jsonify, request, Blueprint
from models import ProteinModel, BindingSiteModel, GeneModel
from db.database import SessionLocal

genomic = Blueprint('genomic', __name__)

@genomic.route('/bindings')
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

@genomic.route('/genes')
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

@genomic.route('/proteins')
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

@genomic.route('/join')
#binding sites - protein
def join():
   #TODO guide on sessions https://docs.sqlalchemy.org/en/13/orm/session_basics.html
   #When to use session and when not?
   session = SessionLocal()

   query = []
   try:
      req_name = request.args.get('protein_name', type=str)

      query = session.query(ProteinModel, BindingSiteModel).filter(ProteinModel.protein_name == req_name).join(BindingSiteModel, ProteinModel.protein_name == BindingSiteModel.protein_name)
      # print('query printing')
      # print(query)
      result = query.all()
   except:
      session.rollback()
      raise
   finally:
      session.close()
   
   #TODO remoove 20 llimit and resolve too big requests somehow   
   return jsonify([{**log.ProteinModel.serialize(), **log.BindingSiteModel.serialize()} for log in result][0:20])
