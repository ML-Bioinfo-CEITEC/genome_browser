from db.import_data_utils import import_binding_sites, import_proteins, import_genes, import_to_prejoin, analyze, cleanup, recreate_all_tables, create_all_tables
from db.import_data_utils import generate_ids_for_bs, decapitate_proteins, decapitate_genes, import_to_prejoin_no_ram

# only for db init
# create_all_tables()

# recreate_all_tables()
# import_binding_sites()
# import_proteins()
# import_genes()
# import_to_prejoin()
# cleanup()

#probably not needed, stats are there already (SELECT * from pg_stats;)
# analyze()


#######################
# generate_ids_for_bs()
# decapitate_proteins()
# decapitate_genes()
#######################
# import_to_prejoin_no_ram()