class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('classe',  pkey='id',name_long='Classe', rowcaption='nome')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('nome', size=':42',name_long='Nome', indexed='y')
        tbl.column('descrizione',name_long='Descrizione')