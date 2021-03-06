# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('article', pkey='id', name_long='!!Article',
                        name_plural='!!Articles')
        self.sysFields(tbl)
        tbl.column('title', name_long='!!Title', indexed='y')
        tbl.column('staff_id', size='22', group='_', name_long='!!Staff id').relation('base.staff.id',
                                                                                      mode='foreignkey')
        tbl.column('description', name_long='!!Description')
        tbl.column('type', size=':6', name_long='!!Type').relation('article_type.code', mode='foreignkey')
