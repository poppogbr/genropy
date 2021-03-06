# -*- coding: UTF-8 -*-

# combobox.py
# Created by Filippo Astolfi on 2010-09-22.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Combobox"""

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage

    def test_1_values(self, pane):
        """Combobox filled through "values" attribute"""
        fb = pane.formbuilder(datapath='test1')
        fb.combobox(value='^.record.values', values='Football,Golf,Karate',
                    lbl='loaded through values')

    def test_2_bag(self, pane):
        """Combobox filled through a Bag"""
        pane.data('.values.sport', self.sports(), id='.pkey', caption='.Description')
        fb = pane.formbuilder(datapath='test.test_2_bag')
        fb.combobox(value='^.record.Bag', storepath='.values.sport',
                    lbl='loaded through Bag')

    def sports(self, **kwargs):
        mytable = Bag()
        mytable['r1.pkey'] = 'SC'
        mytable['r1.Description'] = 'Soccer'
        mytable['r2.pkey'] = 'BK'
        mytable['r2.Description'] = 'Basket'
        mytable['r3.pkey'] = 'TE'
        mytable['r3.Description'] = 'Tennis'
        mytable['r4.pkey'] = 'HK'
        mytable['r4.Description'] = 'Hockey'
        mytable['r5.pkey'] = 'BB'
        mytable['r5.Description'] = 'Baseball'
        mytable['r6.pkey'] = 'SB'
        mytable['r6.Description'] = 'Snowboard'
        return mytable
                    