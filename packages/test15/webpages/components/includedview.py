# -*- coding: UTF-8 -*-

# testcomponent.py
# Created by Francesco Porcari on 2010-09-22.
# Copyright (c) 2010 Softwell. All rights reserved.

"""IncludedView test page"""

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires='gnrcomponents/testhandler:TestHandlerFull,foundation/includedview:IncludedView'

    def common_data(self):
        result = Bag()
        for i in range(5):
            result['r_%i' %i] = Bag(dict(name='Mr. Man %i' %i, age=i+36, work='Work useless %i' %i))
        return result
        
    def common_struct(self,struct):
        r = struct.view().rows()
        r.cell('name', name='Name', width='10em')
        r.cell('age', name='Age', width='5em',dtype='I')
        r.cell('work', name='Work', width='10em')

    def __test_1_includedview_editable_bag(self,pane):
        """Includedview editable datamode bag"""
        bc = pane.borderContainer(height='300px')
        bc.data('.mygrid.rows',self.common_data())
        iv = self.includedViewBox(bc,label='!!Products',datapath='.mygrid',
                            storepath='.rows', struct=self.common_struct, 
                            autoWidth=True,datamode='bag',
                            add_action=True,del_action=True,editorEnabled=True)
        gridEditor = iv.gridEditor()
        gridEditor.textbox(gridcell='name')
        gridEditor.numbertextbox(gridcell='age')
        gridEditor.textbox(gridcell='work')
    
    def test_2_remote_includedview_editable_bag(self,pane):
        """Includedview editable datamode bag"""
        bc = pane.borderContainer(height='300px')
        bc.data('.mygrid.rows',self.common_data())
        bc.contentPane(region='top').button('Build remote grid',fire='.build')
        bc.contentPane(region='center').remote('test_2',_fired='^.build')
    
    def remote_test_2(self,pane):
        bc = pane.borderContainer(height='100%') 
        iv = self.includedViewBox(bc,label='!!Products',datapath='.mygrid',
                            storepath='.rows', struct=self.common_struct, 
                            autoWidth=True,datamode='bag',
                            add_action=True,del_action=True,editorEnabled=True)
        gridEditor = iv.gridEditor()
        gridEditor.textbox(gridcell='name')
        gridEditor.numbertextbox(gridcell='age')
        gridEditor.textbox(gridcell='work')