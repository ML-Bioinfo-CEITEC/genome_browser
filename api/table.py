from flask_table import Table, Col, LinkCol
from flask_table.html import element
from flask import request, url_for

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
    score = ScoreCol("Score")
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