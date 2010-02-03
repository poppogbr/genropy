# encoding: utf-8
import random
import string
from datetime import datetime
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('authorization',  pkey='code',name_long='!!Authorization',
                      name_plural='!!Authorizations')
        self.sysFields(tbl, id=False)
        tbl.column('code', size='8',validate_case='U', name_long='!!Code')
        tbl.column('user_id',size='22',name_long='!!Event').relation('user.id',mode='foreignkey')
        tbl.column('use_ts','DH',name_long='!!Used datetime')
        tbl.column('used_by',size=':32',name_long='!!Used by')
        tbl.column('note',name_long='!!Note')     
        
    def generate_code(self):
        code = ''.join( random.Random().sample(string.letters+string.digits, 8)).upper()
        for c in (('0','M'),('1','N'),('O','X'),('L','Y'),('I','Z')):
            code = code.replace(c[0],c[1])
        return code
                
    def use_auth(self,code,username):
        record = self.record(pkey=code,for_update=True).output('bag')
        record['use_datetime'] =  datetime.now()
        record['used_by'] =  username
        self.update(record)
    
    def check_auth(self,code):
        code = code.upper()
        coupon = self.db.record(pkey=code)
        if not coupon:
            return False
        if coupon['use_datetime']:
            return False
        return True
