from flask import jsonify, request, Blueprint, render_template, url_for, redirect
from models import ProteinModel, BindingSiteModel, GeneModel, PrejoinModel
from db.database import db
from forms import SearchForm
import csv
from flask_csv import send_csv
from api_helpers import get_params_from_request, get_query_from_params, get_params_from_form
from html_content import tooltips

ROWS_PER_PAGE = 20

genomic = Blueprint('genomic', __name__)

@genomic.route('/download')
def download():
   #TODO possible upgrade: what if the data doesnt fit in RAM? change instance_class in yaml https://cloud.google.com/appengine/docs/standard#instance_classes
   params = get_params_from_request(request)
   query = get_query_from_params(params)
   result = query.all()
   if(len(result) == 0):
      return "No results"
   results = [{**log.PrejoinModel.serialize(), "Protein url":log[1], "Symbol url":log[2],} for log in result]

   return send_csv(results,"genomic_download.csv",results[0].keys())

@genomic.route('/', methods=["GET", "POST"])
def search():
   searchform = SearchForm()
   form_params = get_params_from_form(searchform)
   if(searchform.validate_on_submit()):
      return redirect(url_for('genomic.search',page=1,**form_params,))

   params = get_params_from_request(request)
   query = get_query_from_params(params)
   
   pagination = query.paginate(page=params['page'], per_page=ROWS_PER_PAGE)
   serialized=[{**log.PrejoinModel.serialize(), "Protein url":log[1], "Symbol url":log[2]} for log in pagination.items]

   header_keys = serialized[0].keys() if serialized else {}

   args_without_page = {key: value for key, value in request.args.items() if key != 'page'}
   args_without_secondary_sort = {key: value for key, value in request.args.items() if key != 'sort_by_secondary'}
   args_without_primary_sort = {key: value for key, value in request.args.items() if key != 'sort_by'}

   primary_sort_asc_urls = {column: url_for('genomic.search', sort_by=f"{column}_asc", **args_without_primary_sort) for column in header_keys}
   primary_sort_desc_urls = {column: url_for('genomic.search', sort_by=f"{column}_desc", **args_without_primary_sort) for column in header_keys}
   secondary_sort_asc_urls = {column: url_for('genomic.search', sort_by_secondary=f"{column}_asc", **args_without_secondary_sort) for column in header_keys}
   secondary_sort_desc_urls = {column: url_for('genomic.search', sort_by_secondary=f"{column}_desc", **args_without_secondary_sort) for column in header_keys}

   return render_template(
      'index.html',
      rows=serialized, 
      rows_per_page=ROWS_PER_PAGE,
      pages = pagination.pages,
      number_of_results = query.count(),
      tooltips = tooltips,
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

