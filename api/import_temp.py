from db.import_data import import_binding_sites, import_proteins, import_genes, import_to_prejoin, analyze, cleanup

import_binding_sites()
import_proteins()
import_genes()

import_to_prejoin()
cleanup()

#probably not needed, stats are there already (SELECT * from pg_stats;)
# analyze()


#TODO reupload scipt (dont delete tables, just overwrite data)

