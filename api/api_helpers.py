from models import PrejoinModel, ProteinModel
import math
from sqlalchemy.orm import aliased
from sqlalchemy import text, func

def get_params_from_request(request):
   #get parameters from url
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
   params["sortby"] = request.args.get('sort_by', type=str, default='id_asc')
   params["sortby_secondary"] = request.args.get('sort_by_secondary', type=str, default=None)
   
   #sorting by secondary first does nothing (sorting by id is the hidden default), thus this fix
   if(request.args.get('sort_by') == None and request.args.get('sort_by_secondary')!=None):
      params["sortby"] = params["sortby_secondary"]
      params["sortby_secondary"] = None

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
   if(protein): filters.append(func.lower(PrejoinModel.protein_name) == func.lower(protein))
   if(symbol): filters.append(func.lower(PrejoinModel.symbol) == func.lower(symbol))
   if(gene_id): filters.append(func.lower(PrejoinModel.gene_id) == func.lower(gene_id))
   
   if(loc_min): filters.append(PrejoinModel.gene_start >= loc_min)
   if(loc_max): filters.append(PrejoinModel.gene_end <= loc_max)

   #checks if not None and if not empty string
   if(chromozom): filters.append(func.lower(PrejoinModel.chr) == func.lower(chromozom))
   if(area_min): filters.append(PrejoinModel.bs_start >= area_min)
   if(area_max): filters.append(PrejoinModel.bs_end <= area_max)
   if(score_min): filters.append(PrejoinModel.score >= score_min)

   #PREJOINED QUERY
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
   #i display only 3 decimals for score - if i sort by score primarily and secondarily by something else, the table looks weird, because the full score isnt displayed
   if(sortby == 'score_asc'): query = query.order_by(PrejoinModel.score.asc())
   if(sortby == 'score_desc'): query = query.order_by(PrejoinModel.score.desc())

   if(sortby == 'protein_name_asc'): query = query.order_by(PrejoinModel.protein_name.asc())
   if(sortby == 'protein_name_desc'): query = query.order_by(PrejoinModel.protein_name.desc())

   if(sortby == 'chr_asc'): 
      query = query.order_by(text("(substring(chr, '^[0-9]+')::int, substring(chr, '[^0-9]*$')) ASC"))
   if(sortby == 'chr_desc'): 
      query = query.order_by(text("(substring(chr, '^[0-9]+')::int, substring(chr, '[^0-9]*$')) DESC"))

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


   if(sortby == 'id_asc'): query = query.order_by(PrejoinModel.bs_id.asc())
   if(sortby == 'id_desc'): query = query.order_by(PrejoinModel.bs_id.desc())

   if(sortby_secondary):
      if(sortby_secondary == 'score_asc'): query = query.order_by(PrejoinModel.score.asc())
      if(sortby_secondary == 'score_desc'): query = query.order_by(PrejoinModel.score.desc())

      if(sortby_secondary == 'protein_name_asc'): query = query.order_by(PrejoinModel.protein_name.asc())
      if(sortby_secondary == 'protein_name_desc'): query = query.order_by(PrejoinModel.protein_name.desc())

      if(sortby_secondary == 'chr_asc'): 
         query = query.order_by(text("(substring(chr, '^[0-9]+')::int, substring(chr, '[^0-9]*$')) ASC"))
      if(sortby_secondary == 'chr_desc'): 
         query = query.order_by(text("(substring(chr, '^[0-9]+')::int, substring(chr, '[^0-9]*$')) DESC"))

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

def get_params_from_form(searchform):
      form_params = {}
      for fieldname, value in searchform.data.items():
         if value and fieldname!='submit' and fieldname!='csrf_token':
            form_params[fieldname] = value
      return form_params