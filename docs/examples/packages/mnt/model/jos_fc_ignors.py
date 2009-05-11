# encoding: utf-8
from gnr.core.gnrbag import Bag,BagResolver
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('jos_fc_ignors',  pkey='None',name_long='jos_fc_ignors')
        tbl.column('created', dtype ='DH', name_long ='!!Created', notnull ='y')  
        tbl.column('userid', dtype ='I', name_long ='!!Userid')  
        tbl.column('ignoreduserid', dtype ='I', name_long ='!!Ignoreduserid')  
        tbl.column('instance_id', dtype ='I', name_long ='!!Instance_Id')  
