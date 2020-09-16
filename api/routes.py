from flask import jsonify, request, Blueprint, render_template, url_for, redirect
from models import ProteinModel, BindingSiteModel, GeneModel, PrejoinModel
from db.database import db
from forms import SearchForm
from copy import deepcopy
from flask_table import Table, Col, LinkCol
from flask_table.html import element
import csv
from table import MyTable, sort_type_getter
from flask_csv import send_csv
from api_helpers import get_params_from_request, get_query_from_params, Pagination

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

@genomic.route('/search', methods=["POST"])
def search_post():
   searchform = SearchForm()
   params = {}
   for fieldname, value in searchform.data.items():
      #TODO resolve the token in url some other way, why is it in there in the first place?
      if value and fieldname!='submit' and fieldname!='csrf_token':
         params[fieldname] = value

   if(searchform.validate_on_submit()):
      return redirect(url_for('genomic.search',page=1,**params,))

   #TODO non-valid form, alert user?
   return redirect(
         url_for(
            'genomic.search', 
            page=1, 
            **params,
         )
      )

@genomic.route('/search', methods=["GET"])
#TODO what if db is not running -> crashes
#TODO verify attributed, server crashes if wrong arguments supplied, try testing it, wrong datatype etc...
#TODO empty result - crashes in multiple places
#TODO add cache for back button etc?
def search():
   searchform = SearchForm()

   params = get_params_from_request(request)
   query = get_query_from_params(params)

   #TODO dynamic results to fit the page? solve in css
   pagination = Pagination(query, per_page=20)
   serialized = pagination.get_page(params['page'])
   header_keys = serialized[0].keys() if serialized else {}

   args_without_page = {key: value for key, value in request.args.items() if key != 'page'}
   args_without_secondary_sort = {key: value for key, value in request.args.items() if key != 'sort_by_secondary'}
   args_without_primary_sort = {key: value for key, value in request.args.items() if key != 'sort_by'}

   primary_sort_asc_urls = {column: url_for('genomic.search', sort_by=f"{column}_asc", **args_without_primary_sort) for column in header_keys}
   primary_sort_desc_urls = {column: url_for('genomic.search', sort_by=f"{column}_desc", **args_without_primary_sort) for column in header_keys}
   secondary_sort_asc_urls = {column: url_for('genomic.search', sort_by_secondary=f"{column}_asc", **args_without_secondary_sort) for column in header_keys}
   secondary_sort_desc_urls = {column: url_for('genomic.search', sort_by_secondary=f"{column}_desc", **args_without_secondary_sort) for column in header_keys}

   return render_template(
      'test.html',
      rows=serialized, 
      pages = pagination.total_pages,
      has_prev = pagination.has_prev,
      has_next = pagination.has_next,
      prev_page_url = url_for('genomic.search', page=params['page']-1, **args_without_page),
      next_page_url = url_for('genomic.search', page=params['page']+1, **args_without_page),
      download_url = url_for('genomic.download', **dict(request.args.items())),
      primary_sort_asc_urls = primary_sort_asc_urls,
      primary_sort_desc_urls = primary_sort_desc_urls,
      secondary_sort_asc_urls = secondary_sort_asc_urls,
      secondary_sort_desc_urls = secondary_sort_desc_urls,
      form = searchform,
      params = params,
   )

