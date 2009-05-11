#!/usr/bin/env python
# encoding: utf-8
"""
track.py

Created by Saverio Porcari on 2008-01-31.

"""

class Table(object):
   
    def config_db(self, pkg):
        
        tbl =  pkg.table('attivita',  pkey='id',name_long='Track', rowcaption='descrizione', name_plural=u'!!Attività')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('descrizione',size=':25',name_long='!!Descrizione')
        tbl.column('descrizione_en',size=':25',name_long='!!Desc.Inglese')


