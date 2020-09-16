from flask import jsonify, request, Blueprint, render_template, url_for, redirect, make_response, send_file, Response, after_this_request
from models import ProteinModel, BindingSiteModel, GeneModel, PrejoinModel
from db.database import db
from forms import SearchForm
from copy import deepcopy
from flask_table import Table, Col, LinkCol
from flask_table.html import element
import csv
from table import MyTable, sort_type_getter
from sqlalchemy.orm import aliased
import math
import os 
from flask_csv import send_csv

genomic = Blueprint('genomic', __name__)

@genomic.route('/download')
def download():
   #TODO what if the data doesnt fit in RAM?
   params = get_params_from_request(request)
   query = get_query_from_params(params)
   result = query.all()
   if(len(result) == 0):
      return "No results"
   results = [{**log.PrejoinModel.serialize(), "Protein url":log[1], "Symbol url":log[2],} for log in result]

   return send_csv(results,"genomic_download.csv",results[0].keys())

@genomic.route('/search', methods=["GET","POST"])
#TODO what if db is not running -> crashes
#TODO verify attributed, server crashes if wrong arguments supplied, try testing it, wrong datatype etc...
#TODO empty result - crashes in multiple places
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
      return redirect(
         url_for(
            'genomic.search', 
            page=1, 
            **params,
         )
      )

   params = get_params_from_request(request)
   query = get_query_from_params(params)

   #TODO dynamic results to fit the page? solve in css
   pagination = Pagination(query, per_page=20)
   serialized = pagination.get_page(params['page'])

   #TODO refactor args_without_*, ugly
   args_without_page = {key: value for key, value in request.args.items() if key != 'page'}
   args_without_secondary_sort = {key: value for key, value in request.args.items() if key != 'sort_by_secondary'}
   args_without_primary_sort = {key: value for key, value in request.args.items() if key != 'sort_by'}


   if serialized:
      primary_sort_asc_urls = {column: url_for('genomic.search', sort_by=f"{column}_asc", **args_without_primary_sort) for column in serialized[0].keys()}
      primary_sort_desc_urls = {column: url_for('genomic.search', sort_by=f"{column}_desc", **args_without_primary_sort) for column in serialized[0].keys()}
      secondary_sort_asc_urls = {column: url_for('genomic.search', sort_by_secondary=f"{column}_asc", **args_without_secondary_sort) for column in serialized[0].keys()}
      secondary_sort_desc_urls = {column: url_for('genomic.search', sort_by_secondary=f"{column}_desc", **args_without_secondary_sort) for column in serialized[0].keys()}
   else:
      primary_sort_asc_urls = []
      primary_sort_desc_urls = []
      secondary_sort_asc_urls = []
      secondary_sort_desc_urls = []

   #TODO remove???
   if not serialized:
      serialized = [{'id': None, 'protein_name': None, 'chr': None, 'start': None, 'end': None, 'strand': None, 'score': None, 'note': None, 'symbol': None, 'gene_start': None, 'gene_end': None, 'Protein url': None}]

   return render_template(
      'test.html',
      # table = table,
      rows=serialized, 
      page = params['page'], 
      pages = pagination.total_pages,
      prev_page_url = url_for('genomic.search', page=params['page']-1, **args_without_page),
      next_page_url = url_for('genomic.search', page=params['page']+1, **args_without_page),
      download_url = url_for('genomic.download', **dict(request.args.items())),
      primary_sort_asc_urls = primary_sort_asc_urls,
      primary_sort_desc_urls = primary_sort_desc_urls,
      secondary_sort_asc_urls = secondary_sort_asc_urls,
      secondary_sort_desc_urls = secondary_sort_desc_urls,
      has_prev = pagination.has_prev,
      has_next = pagination.has_next,
      form = searchform,
      chromozom_default = params['chromozom'],
      protein_default = params['protein'],
      symbol_default = params['symbol'],
      sort_by_default = params['sortby'],
      area_min_default = params['area_min'],
      area_max_default = params['area_max'],
      loc_min_default = params['loc_min'],
      loc_max_default = params['loc_max'],
      score_min_default = params['score_min'],
      gene_id_default = params['gene_id'],
   )

def get_params_from_request(request):
   #get parameters from url

   #TODO in progress non-null params
   # params_to_watch = ['protein_name', 'chromozom', 'sort_by', 'page']

   params = {}
   #protein
   params["protein"] = request.args.get('protein_name', type=str, default="")
   params["symbol"] = request.args.get('symbol', type=str, default="")
   params["gene_id"] = request.args.get('gene_id', type=str, default="")

   #genomic location (genes start/end)
   params["loc_min"] = request.args.get('loc_min', type=int, default="")
   params["loc_max"] = request.args.get('loc_max', type=int, default="")
   #chromozom
   params["chromozom"] = request.args.get('chromozom', type=str, default="")
   #gene area (binding site start/end ?)
   params["area_min"] = request.args.get('area_min', type=int, default="")
   params["area_max"] = request.args.get('area_max', type=int, default="")
   #score ?
   params["score_min"] = request.args.get('score_min', type=float, default="")
   # score_max = request.args.get('score_max', type=float)

   #control elements
   params["page"] = request.args.get('page', type=int, default = 1)
   #TODO sorting by secondary first does nothing (sorting by id is the hidden default)
   params["sortby"] = request.args.get('sort_by', type=str, default='id_desc')
   params["sortby_secondary"] = request.args.get('sort_by_secondary', type=str, default=None)

   return params

def get_query_from_params(params):
   protein = params['protein']
   symbol = params['symbol']
   gene_id = params['gene_id']
   loc_min = params['loc_min']
   loc_max = params['loc_max']
   chromozom = params['chromozom']
   area_min = params['area_min']
   area_max = params['area_max']
   score_min = params['score_min']
   sortby = params['sortby']
   sortby_secondary = params['sortby_secondary']

   #building the filters from parameters
   filters = []
   if(protein): filters.append(PrejoinModel.protein_name == protein)
   if(symbol): filters.append(PrejoinModel.symbol == symbol)
   if(gene_id): filters.append(PrejoinModel.gene_id == gene_id)
   
   if(loc_min): filters.append(PrejoinModel.gene_start >= loc_min)
   if(loc_max): filters.append(PrejoinModel.gene_end <= loc_max)

   #checks if not None and if not empty string
   if(chromozom): filters.append(PrejoinModel.chr == chromozom)
   if(area_min): filters.append(PrejoinModel.bs_start >= area_min)
   if(area_max): filters.append(PrejoinModel.bs_end <= area_max)
   if(score_min): filters.append(PrejoinModel.score >= score_min)
   # if(score_max!=None): filters.append(BindingSiteModel.score <= score_max)

   #ON-LINE QUERY
   #TODO sorting by id doesnt give me all the ids (with no filters) - are we filtering wrong?
   # query = BindingSiteModel.query.join(ProteinModel, ProteinModel.protein_name == BindingSiteModel.protein_name)
   # query = query.join(GeneModel, (GeneModel.strand == BindingSiteModel.strand) & (GeneModel.chr == BindingSiteModel.chr) & (BindingSiteModel.end > GeneModel.start) & (BindingSiteModel.start < GeneModel.end))
   # query = query.add_columns(GeneModel.symbol, GeneModel.start, GeneModel.end, ProteinModel.uniprot_url)
   #TODO Gene and binding site ranges ---  >= or > ?


   #PREJOINED QUERY
   #TODO add symbol url
   p1 = aliased(ProteinModel)
   p2 = aliased(ProteinModel)

   query = PrejoinModel.query
   query = query.outerjoin(p1, p1.protein_name == PrejoinModel.protein_name)
   query = query.outerjoin(p2, p2.protein_name == PrejoinModel.symbol)
   query = query.with_entities(PrejoinModel, p1.uniprot_url, p2.uniprot_url)

   #Filtering
   query = query.filter(*filters)

   #sorting
   #TODO make another argument direction (desc, asc), instead of hardcoding every combination
   #TODO i display only 3 decimals for score - if i sort by score primarily and secondarily by something else, the table looks weird, because the full score isnt displayed
   if(sortby == 'score_asc'): query = query.order_by(PrejoinModel.score.asc())
   if(sortby == 'score_desc'): query = query.order_by(PrejoinModel.score.desc())

   if(sortby == 'protein_name_asc'): query = query.order_by(PrejoinModel.protein_name.asc())
   if(sortby == 'protein_name_desc'): query = query.order_by(PrejoinModel.protein_name.desc())

   if(sortby == 'chr_asc'): query = query.order_by(PrejoinModel.chr.asc())
   if(sortby == 'chr_desc'): query = query.order_by(PrejoinModel.chr.desc())

   if(sortby == 'start_asc'): query = query.order_by(PrejoinModel.bs_start.asc())
   if(sortby == 'start_desc'): query = query.order_by(PrejoinModel.bs_start.desc())

   if(sortby == 'end_asc'): query = query.order_by(PrejoinModel.bs_end.asc())
   if(sortby == 'end_desc'): query = query.order_by(PrejoinModel.bs_end.desc())

   if(sortby == 'strand_asc'): query = query.order_by(PrejoinModel.strand.asc())
   if(sortby == 'strand_desc'): query = query.order_by(PrejoinModel.strand.desc())
  
   if(sortby == 'symbol_asc'): query = query.order_by(PrejoinModel.symbol.asc())
   if(sortby == 'symbol_desc'): query = query.order_by(PrejoinModel.symbol.desc())

   if(sortby == 'gene_start_asc'): query = query.order_by(PrejoinModel.gene_start.asc())
   if(sortby == 'gene_start_desc'): query = query.order_by(PrejoinModel.gene_start.desc())

   if(sortby == 'gene_end_asc'): query = query.order_by(PrejoinModel.gene_end.asc())
   if(sortby == 'gene_end_desc'): query = query.order_by(PrejoinModel.gene_end.desc())

   # if(sortby == 'id_asc'): query = query.order_by(BindingSiteModel.id.asc())
   # if(sortby == 'id_desc'): query = query.order_by(BindingSiteModel.id.desc())

   if(sortby == 'id_asc'): query = query.order_by(PrejoinModel.bs_id.asc())
   if(sortby == 'id_desc'): query = query.order_by(PrejoinModel.bs_id.desc())

   if(sortby_secondary):
      if(sortby_secondary == 'score_asc'): query = query.order_by(PrejoinModel.score.asc())
      if(sortby_secondary == 'score_desc'): query = query.order_by(PrejoinModel.score.desc())

      if(sortby_secondary == 'protein_name_asc'): query = query.order_by(PrejoinModel.protein_name.asc())
      if(sortby_secondary == 'protein_name_desc'): query = query.order_by(PrejoinModel.protein_name.desc())

      # if(sortby_secondary == 'protein_name_asc'): query = query.order_by(BindingSiteModel.protein_name.asc())
      # if(sortby_secondary == 'protein_name_desc'): query = query.order_by(BindingSiteModel.protein_name.desc())

      if(sortby_secondary == 'chr_asc'): query = query.order_by(PrejoinModel.chr.asc())
      if(sortby_secondary == 'chr_desc'): query = query.order_by(PrejoinModel.chr.desc())

      if(sortby_secondary == 'start_asc'): query = query.order_by(PrejoinModel.bs_start.asc())
      if(sortby_secondary == 'start_desc'): query = query.order_by(PrejoinModel.bs_start.desc())

      if(sortby_secondary == 'end_asc'): query = query.order_by(PrejoinModel.bs_end.asc())
      if(sortby_secondary == 'end_desc'): query = query.order_by(PrejoinModel.bs_end.desc())

      if(sortby_secondary == 'strand_asc'): query = query.order_by(PrejoinModel.strand.asc())
      if(sortby_secondary == 'strand_desc'): query = query.order_by(PrejoinModel.strand.desc())
   
      if(sortby_secondary == 'symbol_asc'): query = query.order_by(PrejoinModel.symbol.asc())
      if(sortby_secondary == 'symbol_desc'): query = query.order_by(PrejoinModel.symbol.desc())

      if(sortby_secondary == 'gene_start_asc'): query = query.order_by(PrejoinModel.gene_start.asc())
      if(sortby_secondary == 'gene_start_desc'): query = query.order_by(PrejoinModel.gene_start.desc())

      if(sortby_secondary == 'gene_end_asc'): query = query.order_by(PrejoinModel.gene_end.asc())
      if(sortby_secondary == 'gene_end_desc'): query = query.order_by(PrejoinModel.gene_end.desc())

      if(sortby_secondary == 'id_asc'): query = query.order_by(PrejoinModel.bs_id.asc())
      if(sortby_secondary == 'id_desc'): query = query.order_by(PrejoinModel.bs_id.desc())

   return query

#TODO extract to file
class Pagination():
      def __init__(self, query, per_page):
         self.per_page = per_page
         self.query = query

      def get_page(self, page):
         all_results = self.query.all()
         self.total_pages = int(math.ceil(len(all_results)/self.per_page))
         self.has_prev = page > 1
         self.has_next = page < self.total_pages   

         pagination = all_results[self.per_page*(page - 1):self.per_page*page]
         serialized=[{**log.PrejoinModel.serialize(), "Protein url":log[1], "Symbol url":log[2]} for log in pagination]
         return serialized
