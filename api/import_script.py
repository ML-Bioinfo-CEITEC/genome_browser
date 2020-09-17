from db.import_data_utils import import_binding_sites, import_proteins, import_genes, import_to_prejoin, analyze, cleanup, recreate_all_tables

recreate_all_tables()
import_binding_sites()
import_proteins()
import_genes()
import_to_prejoin()
cleanup()

#probably not needed, stats are there already (SELECT * from pg_stats;)
# analyze()