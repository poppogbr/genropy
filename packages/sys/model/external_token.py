# encoding: utf-8
from datetime import datetime
from gnr.core.gnrbag import Bag

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('message',  pkey='id',name_long='!!Messages',
                      name_plural='!!Messages')
        tbl.column('id',size='22',name_long='!!id')
        tbl.column('datetime','DH',name_long='!!Date and Time')
        tbl.column('expiry','DH',name_long='!!Expiry')
        tbl.column('user',size=':32',name_long='!!Destination user',indexed=True)
        tbl.column('connection_id',size='22',name_long='!!Connection Id',indexed=True)
        tbl.column('max_usages','I',name_long='!!Max uses')
        tbl.column('allowed_host',name_long='!!Allowed host')
        tbl.column('page_path',name_long='!!Page path')
        tbl.column('method',name_long='!!Method')
        tbl.column('parameters',dtype='X',name_long='!!Parameters')


    def create_token(self,page_path,expiry=None,allowed_host=None, user=None,
                connection_id=None,max_usages=None,method=None,parameters=None):
        record = dict(
            page_path=page_path,
            expiry=expiry,
            allowed_host=allowed_host,
            user=user,
            connection_id=connection_id,
            max_usages=max_usages,
            method=method,
            parameters=Bag(parameters))
        self.insert(record)
        return record['id']
        
    def use_token(self, token, host=None):
        record = self.record(id=token) or Bag()
        # if host .... check if is equal ...
        record = self.check_token(record, host) 
        if record:
            self.db.table('sys.external_token_use').insert(dict(external_token_id=record['id'],host=host,datetime=datetime.now()))
            return record['method'],[],dict(record['parameters'] or {})
        return None, None, None
    
    def check_token(self,record,host=None):
        if host:
            pass
        if record['expiry']>=datetime.now():
            return None
        if record['max_usages']:
            uses = self.db.table('sys.external_token_use').query(where='external_token_id := id',id=record['id']).count()
            if uses > record['max_usages']:
                return None
        return record
        