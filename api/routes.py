from flask import jsonify, request, Blueprint, render_template, url_for, redirect
from models import ProteinModel, BindingSiteModel, GeneModel
from db.database import db
from forms import SearchForm
from copy import deepcopy

genomic = Blueprint('genomic', __name__)

@genomic.route('/search', methods=["GET","POST"])
#TODO what if db is not running -> crashes
#TODO verify attributed, server crashes if wrong arguments supplied, try testing it, wrong datatype etc...
#TODO empty result - crashes
#TODO convert to POST request (has body) on searching, so params don't clutter url bar
#TODO add cache for back button etc?
def search():
   #check for search form sumbission
   searchform = SearchForm()

   #If form is not valid, this if is False!!! 
   if(searchform.validate_on_submit()):
      params = {}
      for fieldname, value in searchform.data.items():
         #TODO resolve the token in url some other way, why is it in there in the first place?
         if value and fieldname!='submit' and fieldname!='csrf_token':
            params[fieldname] = value
            print(fieldname, value)
      return redirect(
         url_for(
            'genomic.search', 
            page=1, 
            **params,
         )
      )

   #get parameters from url

   #TODO in progress non-null params
   
   params_to_watch = ['protein_name', 'chromozom', 'sort_by', 'page']


   #protein
   protein = request.args.get('protein_name', type=str, default="")
   #genomic location (genes start/end)
   loc_min = request.args.get('loc_min', type=int, default="")
   loc_max = request.args.get('loc_max', type=int, default="")
   #chromozom
   chromozom = request.args.get('chromozom', type=str, default="")
   #gene area (binding site start/end ?)
   area_min = request.args.get('area_min', type=int, default="")
   area_max = request.args.get('area_max', type=int, default="")
   #score ?
   score_min = request.args.get('score_min', type=float)
   score_max = request.args.get('score_max', type=float)

   #control elements
   page = request.args.get('page', type=int, default = 1)
   sortby = request.args.get('sort_by', type=str, default='protein_name_desc')

   #building the filters from parameters
   filters = []
   if(protein): filters.append(ProteinModel.protein_name == protein)
   
   if(loc_min): filters.append(GeneModel.start >= loc_min)
   if(loc_max): filters.append(GeneModel.end <= loc_max)

   #checks if not None and if not empty string
   if(chromozom): filters.append(BindingSiteModel.chr == chromozom)
   if(area_min): filters.append(BindingSiteModel.start >= area_min)
   if(area_max): filters.append(BindingSiteModel.end <= area_max)
   if(score_min!=None): filters.append(BindingSiteModel.score >= score_min)
   if(score_max!=None): filters.append(BindingSiteModel.score <= score_max)

   
   #bulding the query 
   #Legacy query - querying all models, not only binding site
   #TODO order joins properly
   # query = db.session.query(BindingSiteModel, ProteinModel.protein_name, GeneModel.symbol)
   # query = query.join(ProteinModel, ProteinModel.protein_name == BindingSiteModel.protein_name)
   # query = query.join(GeneModel, GeneModel.chr == BindingSiteModel.chr)
   # query = query.filter(*filters)

   query = BindingSiteModel.query.join(ProteinModel, ProteinModel.protein_name == BindingSiteModel.protein_name)
   query = query.join(GeneModel, (GeneModel.symbol == BindingSiteModel.protein_name) & (GeneModel.chr == BindingSiteModel.chr))
   #TODO uncomment this later, in testing dataset, there are no fitting datapoints  ,>= or > ?
      # & (BindingSiteModel.end > GeneModel.start) & (BindingSiteModel.start < GeneModel.end))

   query = query.add_columns(GeneModel.symbol, GeneModel.start, GeneModel.end)
   query = query.filter(*filters)

   #sorting
   #.desc() is redundant?
   if(sortby == 'score_desc'): query = query.order_by(BindingSiteModel.score.desc())
   if(sortby == 'protein_name_desc'): query = query.order_by(BindingSiteModel.protein_name.desc())
   if(sortby == 'score_asc'): query = query.order_by(BindingSiteModel.score.asc())
   if(sortby == 'protein_name_asc'): query = query.order_by(BindingSiteModel.protein_name.asc())

   # print(query)

   pagination = query.paginate(page=page, per_page = 25)
   
   #TODO remove gene start and end, it's there just for our check
   serialized = [{**log.BindingSiteModel.serialize(), "Gene symbol":log[1], "Gen start":log[2], "Gen end":log[3]} for log in pagination.items]

   #TODO hacking is my life
   #resolve all defaults this way and don't pass to html?
   if area_min == None:
      area_min = ''
   if area_max == None:
      area_max = ''
   if loc_min == None:
      loc_min = ''
   if loc_max == None:
      loc_max = ''
   searchform.sort_by.data = sortby

   args_without_page = {key: value for key, value in request.args.items() if key != 'page'}

   return render_template(
      'test.html', 
      rows=serialized, 
      page = page, 
      pages = pagination.pages,
      #TODO add other parameters
      prev_page_url = url_for('genomic.search', page=page-1, **args_without_page),
      next_page_url = url_for('genomic.search', page=page+1, **args_without_page),
      has_prev = pagination.has_prev,
      has_next = pagination.has_next,
      form = searchform,
      chromozom_default = chromozom,
      protein_default = protein,
      sort_by_default = sortby,
      area_min_default = area_min,
      area_max_default = area_max,
      loc_min_default = loc_min,
      loc_max_default = loc_max,
   )
