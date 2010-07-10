#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

""" dbSelect """
import os
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace, splitAndStrip, countOf

class GnrCustomWebPage(object):
    css_requires='index.css'   
    def main(self, root, **kwargs):
        cont = root.div(_class='fieldcontainer',margin='1em',padding='10px',datapath='table')
        tbl=cont.table()
        r=tbl.tr()
        r.td('Star name')
        r.td().field('showcase.person.name')