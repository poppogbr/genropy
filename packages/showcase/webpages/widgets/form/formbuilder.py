#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    css_requires= 'index'
    
    def main(self, root, **kwargs):
        root.div('----- Example of Form builder ------',_class='infopar')
        root.div('note in data source that the following textbox has a RELATIVE path',
                  _class='infopar')
        fb=root.formbuilder(cols=3,datapath='record')
        fb.textbox(lbl='Name',value='^.name')
        fb.textbox(lbl='Surname',value='^.surname',colspan=2)
        fb.numberTextbox(lbl="Age",value='^.age',width='4em')
        fb.filteringSelect(lbl='Sex',value='^.sex',colspan=2,values='M:Male,F:Female')
        fb.textbox(lbl='Job',value='^.job.profession')
        fb.textbox(lbl='Company name',value='^.job.company_name')
        root.div('------ Example of table ------',_class='infopar')
        d = root.div(_class='infopar')
        d.span('What you write in a magic div appear in the other one and vice versa')
        d2 = root.div(_class='infopar') 
        d2.span('The following divs have an ABSOLUTE path')
        table = root.table().tbody()
        r1 = table.tr()
        r1.td('Phone number')
        r1.td().textbox(value='^phone_number')
        r2 = table.tr()
        r2.td('Magic div 1')
        r2.td().textbox(value='^magic')
        r2.td('Magic div 2')
        r2.td().textbox(value='^magic')