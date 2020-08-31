from flask import jsonify, request, Blueprint, render_template, url_for, redirect, make_response, send_file
from models import ProteinModel, BindingSiteModel, GeneModel
from db.database import db
from forms import SearchForm
from copy import deepcopy
from flask_table import Table, Col, LinkCol
from flask_table.html import element
import csv

genomic = Blueprint('genomic', __name__)

@genomic.route('/download')
def download():
   #TODO what if the data doesnt fit in RAM?

   params = get_params_from_request(request)
   query = get_query_from_params(params)
   result = query.all()
   
   results = [{**log.BindingSiteModel.serialize(), "symbol":log[1], "gene_start":log[2], "gene_end":log[3], "Protein url":log[4]} for log in result]
   if(len(results) == 0):
      return "No results"

   #TODO skip undesired keys
   keys = results[0].keys()
   #TODO delete csv afterwards?
   with open('genomic_download.csv', 'w', newline='') as output_file:
      dict_writer = csv.DictWriter(output_file, keys)
      dict_writer.writeheader()
      dict_writer.writerows(results)

   return send_file('genomic_download.csv', mimetype='text/csv',
                     attachment_filename='genomic_dowload.csv',
                     as_attachment=True)

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

   params = get_params_from_request(request)
   query = get_query_from_params(params)
   # print(query)

   #TODO duplicate 
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
   page = params['page']

   pagination = query.paginate(page=page, per_page = 25)
   
   #TODO remove gene start and end, it's there just for our check
   serialized = [{**log.BindingSiteModel.serialize(), "symbol":log[1], "gene_start":log[2], "gene_end":log[3], "Protein url":log[4]} for log in pagination.items]

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
   if score_min == None:
      score_min = ''

   args_without_page = {key: value for key, value in request.args.items() if key != 'page'}



   #TABLECODE#################
   #TODO extract elswhere
   class ExternalUrlCol(Col):
      def __init__(self, name, url_attr, **kwargs):
         self.url_attr = url_attr
         super(ExternalUrlCol, self).__init__(name, **kwargs)

      def td_contents(self, item, attr_list):
         text = self.from_attr_list(item, attr_list)
         url = self.from_attr_list(item, [self.url_attr])
         return element('a', {'href': url}, content=text)

   class ScoreCol(Col):
      def td_contents(self, item, attr_list):
         return element('div', content=round(self.from_attr_list(item, 'score'), 3))

   class MyTable(Table):
      allow_sort = True
      id=Col("Id")
      protein_name = ExternalUrlCol(name="Protein name", url_attr='Protein url', attr='protein_name')
      score = ScoreCol("Score", )
      chr=Col("Chromozom")
      start=Col("Start")
      end=Col("End")
      strand=Col("Strand")
      note=Col("Note")
      symbol=ExternalUrlCol(name="Gene symbol", url_attr='Protein url', attr='symbol')
      gene_start=Col("Gene start")
      gene_end=Col("Gene end")

      def __init__(self, items, request, last_sort_type, html_attrs):
         self.last_sort_type = last_sort_type
         Table.__init__(self, items=items, html_attrs = html_attrs)

      def sort_url(self, col_key, reverse=False):
         args_without_sortby = {key: value for key, value in request.args.items() if key != 'sort_by'}


         if(self.last_sort_type == 'asc'):
            suffix = 'desc'
         if(self.last_sort_type == 'desc'):
            suffix = 'asc'

         return url_for('genomic.search', **args_without_sortby, sort_by=col_key+'_'+suffix)


   
   sort_type_getter = {
      'score_desc': 'desc',
      'protein_name_desc': 'desc',
      'chr_desc':'desc',
      'start_desc':'desc',
      'end_desc':'desc',
      'strand_desc':'desc',
      'symbol_desc':'desc',
      'gene_start_desc':'desc',
      'gene_end_desc':'desc',
      'id_desc':'desc',

      'score_asc':'asc',
      'protein_name_asc':'asc',
      'chr_asc':'asc',
      'start_asc':'asc',
      'end_asc':'asc',
      'strand_asc':'asc',
      'symbol_asc':'asc',
      'gene_start_asc':'asc',
      'gene_end_asc':'asc',
      'id_asc':'asc'
   }

   table = MyTable(
      # items=[{'protein_name': log['protein_name'], 'score':log['score'], 'chr':log['chr']} for log in serialized],
      items=serialized,
      request = request,
      last_sort_type=sort_type_getter[sortby],
      html_attrs={'style':'width:100%','border':'1px solid lightgrey'}
   )
   #TODO check the validity of sortby existing in dict
   # table.set_last_sort(sort_type_getter[sortby])
   #####################

   return render_template(
      'test.html', 
      table = table,
      rows=serialized, 
      page = page, 
      pages = pagination.pages,
      #TODO add other parameters
      prev_page_url = url_for('genomic.search', page=page-1, **args_without_page),
      next_page_url = url_for('genomic.search', page=page+1, **args_without_page),
      download_url = url_for('genomic.download', **dict(request.args.items())),
      has_prev = pagination.has_prev,
      has_next = pagination.has_next,
      form = searchform,
      chromozom_default = chromozom,
      protein_default = protein,
      symbol_default = symbol,
      sort_by_default = sortby,
      area_min_default = area_min,
      area_max_default = area_max,
      loc_min_default = loc_min,
      loc_max_default = loc_max,
      score_min_default = score_min,
      gene_id_default = gene_id,
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
   params["sortby"] = request.args.get('sort_by', type=str, default='protein_name_desc')

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

   #building the filters from parameters
   filters = []
   if(protein): filters.append(ProteinModel.protein_name == protein)
   if(symbol): filters.append(GeneModel.symbol == symbol)
   if(gene_id): filters.append(GeneModel.id == gene_id)
   
   if(loc_min): filters.append(GeneModel.start >= loc_min)
   if(loc_max): filters.append(GeneModel.end <= loc_max)

   #checks if not None and if not empty string
   if(chromozom): filters.append(BindingSiteModel.chr == chromozom)
   if(area_min): filters.append(BindingSiteModel.start >= area_min)
   if(area_max): filters.append(BindingSiteModel.end <= area_max)
   if(score_min): filters.append(BindingSiteModel.score >= score_min)
   # if(score_max!=None): filters.append(BindingSiteModel.score <= score_max)

   
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

   #TODO why do we display gene symbol (its the same as protein name always, we are joining on that!)
   query = query.add_columns(GeneModel.symbol, GeneModel.start, GeneModel.end, ProteinModel.uniprot_url)
   query = query.filter(*filters)

   #sorting
   #TODO make another argument direction (desc, asc), instead of hardcoding every combination
   if(sortby == 'score_asc'): query = query.order_by(BindingSiteModel.score.asc())
   if(sortby == 'score_desc'): query = query.order_by(BindingSiteModel.score.desc())

   if(sortby == 'protein_name_asc'): query = query.order_by(BindingSiteModel.protein_name.asc())
   if(sortby == 'protein_name_desc'): query = query.order_by(BindingSiteModel.protein_name.desc())

   if(sortby == 'chr_asc'): query = query.order_by(GeneModel.chr.asc())
   if(sortby == 'chr_desc'): query = query.order_by(GeneModel.chr.desc())

   if(sortby == 'start_asc'): query = query.order_by(BindingSiteModel.start.asc())
   if(sortby == 'start_desc'): query = query.order_by(BindingSiteModel.start.desc())

   if(sortby == 'end_asc'): query = query.order_by(BindingSiteModel.end.asc())
   if(sortby == 'end_desc'): query = query.order_by(BindingSiteModel.end.desc())

   if(sortby == 'strand_asc'): query = query.order_by(BindingSiteModel.strand.asc())
   if(sortby == 'strand_desc'): query = query.order_by(BindingSiteModel.strand.desc())
  
   if(sortby == 'symbol_asc'): query = query.order_by(GeneModel.symbol.asc())
   if(sortby == 'symbol_desc'): query = query.order_by(GeneModel.symbol.desc())

   if(sortby == 'gene_start_asc'): query = query.order_by(GeneModel.start.asc())
   if(sortby == 'gene_start_desc'): query = query.order_by(GeneModel.start.desc())

   if(sortby == 'gene_end_asc'): query = query.order_by(GeneModel.end.asc())
   if(sortby == 'gene_end_desc'): query = query.order_by(GeneModel.end.desc())

   if(sortby == 'id_asc'): query = query.order_by(BindingSiteModel.id.asc())
   if(sortby == 'id_desc'): query = query.order_by(BindingSiteModel.id.desc())

   return query