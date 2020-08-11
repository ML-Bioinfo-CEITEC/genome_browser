from flask import jsonify, request, Blueprint, render_template, url_for, redirect
from models import ProteinModel, BindingSiteModel, GeneModel
from db.database import db
from forms import SearchForm

genomic = Blueprint('genomic', __name__)

@genomic.route('/search', methods=["GET","POST"])
#TODO what if db is not running -> crashes
#TODO verify attributed, server crashes if wrong arguments supplied, try testing it, wrong datatype etc...
#TODO empty result - crashes
#TODO convert to POST request (has body) on searching, so params don't clutter url bar
#TODO csrf token in url - takes space
def search():
   #check for search form sumbission
   searchform = SearchForm()
   if(searchform.validate_on_submit()):
      params = {}
      for fieldname, value in searchform.data.items():
         if value and fieldname!='submit':
            params[fieldname] = value
      return redirect(
         url_for(
            'genomic.search', 
            page=1, 
            **params,
         )
      )

   #get parameters from url
   #protein
   protein = request.args.get('protein_name', type=str, default="")
   #genomic location (genes start/end)
   loc_min = request.args.get('loc_min', type=int)
   loc_max = request.args.get('loc_max', type=int)
   #chromozom
   chromozom = request.args.get('chromozom', type=str, default="")
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
   if(protein): filters.append(ProteinModel.protein_name == protein)
   
   if(loc_min!=None): filters.append(GeneModel.start >= loc_min)
   if(loc_max!=None): filters.append(GeneModel.end <= loc_max)

   #checks if not None and if not empty string
   if(chromozom): filters.append(BindingSiteModel.chr == chromozom)
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
   # print(len(pagination.items))

   if(len(pagination.items) == 0):
      return "No results found bruh \n" + str(query )

   serialized = [log.serialize() for log in pagination.items]
   return render_template(
      'test.html', 
      rows=serialized, 
      page = page, 
      pages = pagination.pages,
      #TODO add other parameters
      #TODO if next/prev page exists
      prev_page_url = url_for('genomic.search', page=page-1, chromozom=chromozom, protein_name=protein),
      next_page_url = url_for('genomic.search', page=page+1, chromozom=chromozom, protein_name=protein),
      form = searchform,
      chromozom_default = chromozom,
      protein_default = protein,
   )
