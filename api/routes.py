from flask import jsonify, request, Blueprint, render_template
from models import ProteinModel, BindingSiteModel, GeneModel
from db.database import db

genomic = Blueprint('genomic', __name__)

@genomic.route('/bindings', methods=['GET'])
def bindings():
   #range search - use query(x).filter(x.id.in_([1,3]))
   req_id = request.args.get('id', type=int)
   req_min = request.args.get('min', type=int)
   req_max = request.args.get('max', type=int)
   req_score_min = request.args.get('score_min', type=float)
   req_score_max = request.args.get('score_max', type=float)
   page = request.args.get('page', type=int, default = 1)

   sortby = request.args.get('sortby', type=str, default="protein_name")

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
   
   if(sortby == 'score'):
      result = result.order_by(BindingSiteModel.score.desc())

   if(sortby == "protein_name"):
      #.desc() is redundant?
      result = result.order_by(BindingSiteModel.protein_name.desc())

   pagination = result.paginate(page = page, per_page = 10)
   serialized = [log.serialize() for log in pagination.items]
   return render_template('test.html', rows=serialized, page = page, pages = pagination.pages)
   # return jsonify(serialized)

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

#TODO verify attributed, server crashes if wrong arguments supplied, try testing it, wrong datatype etc...
@genomic.route('/join')
#binding sites - protein
def join():
   req_name = request.args.get('protein_name', type=str)
   page = request.args.get('page', type=int, default=1)
   query = db.session.query(ProteinModel, BindingSiteModel).filter(ProteinModel.protein_name == req_name).join(BindingSiteModel, ProteinModel.protein_name == BindingSiteModel.protein_name)
   # print('query printing')
   # print(query)

#    result = query.all()
   pagination = query.paginate(page=page, per_page=4)
   result = pagination.items
   results_dicts_array = [{**log.ProteinModel.serialize(), **log.BindingSiteModel.serialize()} for log in result]
   # total_page_info = {'total_pages':pagination.pages}
#    return jsonify([total_page_info] + results_dicts_array)
   return render_template('test.html', rows=results_dicts_array, page=page, pages=pagination.pages)

@genomic.route('/search', methods=["GET"])
#TODO what if db is not running -> crashes
#TODO empty result - crashes
def search():
   #protein
   protein = request.args.get('protein_name', type=str)
   #genomic location (genes start/end)
   loc_min = request.args.get('loc_min', type=int)
   loc_max = request.args.get('loc_max', type=int)
   #chromozom
   chromozom = request.args.get('chr', type=str)
   #gene area (binding site start/end ?)
   area_min = request.args.get('area_min', type=int)
   area_max = request.args.get('area_max', type=int)
   #score ?
   score_min = request.args.get('score_min', type=float)
   score_max = request.args.get('score_max', type=float)

   #control elements
   page = request.args.get('page', type=int, default = 1)
   sortby = request.args.get('sort_by', type=str, default="protein_name")

   #building the filters from parameters
   filters = []
   if(protein!=None): filters.append(ProteinModel.protein_name == protein)
   
   if(loc_min!=None): filters.append(GeneModel.start >= loc_min)
   if(loc_max!=None): filters.append(GeneModel.end <= loc_max)

   if(chromozom!=None): filters.append(BindingSiteModel.chr == chromozom)
   if(area_min!=None): filters.append(BindingSiteModel.start >= area_min)
   if(area_max!=None): filters.append(BindingSiteModel.end <= area_max)
   if(score_min!=None): filters.append(BindingSiteModel.score >= score_min)
   if(score_max!=None): filters.append(BindingSiteModel.score <= score_max)

   #bulding the query
   #Legacy query - querying all models, not only binding site
   #TODO when i query(ProteinModel) only, i get only 1 on page and multiple results, wtf?
   #TODO order joins properly
   # query = db.session.query(ProteinModel, BindingSiteModel, GeneModel)
   # query = query.join(BindingSiteModel, ProteinModel.protein_name == BindingSiteModel.protein_name)
   # query = query.join(GeneModel, GeneModel.chr == BindingSiteModel.chr)
   # query = query.filter(*filters)

   query = BindingSiteModel.query.join(ProteinModel, ProteinModel.protein_name == BindingSiteModel.protein_name)
   query = query.join(GeneModel, GeneModel.symbol == BindingSiteModel.protein_name)
   # query = query.distinct(BindingSiteModel.id)
   query = query.filter(*filters)

   #sorting
   #.desc() is redundant?
   if(sortby == 'score'): query = query.order_by(BindingSiteModel.score.desc())
   if(sortby == "protein_name"): query = query.order_by(BindingSiteModel.protein_name.desc())

   # print(query)

   pagination = query.paginate(page=page, per_page = 25)
   print(len(pagination.items))
   serialized = [log.serialize() for log in pagination.items]
   return render_template('test.html', rows=serialized, page = page, pages = pagination.pages)
