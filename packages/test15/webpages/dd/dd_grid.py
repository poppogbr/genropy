# -*- coding: UTF-8 -*-

# batch_handler.py
# Created by Francesco Porcari on 2010-10-01.
# Copyright (c) 2010 Softwell. All rights reserved.


"""Grid with drag & drop"""

from gnr.core.gnrbag import Bag, DirectoryResolver
import datetime
class GnrCustomWebPage(object):

    py_requires="""gnrcomponents/testhandler:TestHandlerFull"""
    def test_0_drop(self,pane):
        """Drop Boxes"""
        fb=pane.formbuilder(cols=1)
        dropboxes=fb.div(drop_action='console.log("ddd");alert(drop_data)',lbl='Drop boxes text/plain',drop_types='text/plain')
                            
        dropboxes.div('no tags',width='100px',height='50px',margin='3px',background_color='#c7ff9a',
                            float='left',droppable=True)
        dropboxes.div('only foo',width='100px',height='50px',margin='3px',background_color='#fcfca9',
                            float='left',drop_tags='foo',droppable=True)
        dropboxes.div('only bar',width='100px',height='50px',margin='3px',background_color='#ffc2f5',
                            float='left',drop_tags='bar',droppable=True)
        dropboxes.div('only foo AND bar',width='100px',height='50px',margin='3px',background_color='#a7cffb',
                            float='left',drop_tags='foo AND bar',droppable=True)
        
        
    def test_1_grid(self,pane):
        pane=pane.div(height='300px')
        pane.data('.data',self.aux_test_1_grid_data())
        grid = pane.IncludedView(nodeId='inputgrid',storepath='.data',
                        datamode='bag',editorEnabled=True)
                        
        gridEditor = grid.gridEditor(datapath='dummy') #editOn='onCellClick')
        gridEditor.filteringSelect(gridcell='filter',values='A:Alberto,B:Bonifacio,C:Carlo')
        gridEditor.dbSelect(dbtable='devlang.language',gridcell='language',hasDownArrow=True,autoComplete=True,
                            value='^.language_id',validate_notnull=True,validate_notnull_error='!!Required')
        gridEditor.textbox(gridcell='name',validate_len='4:7',validate_len_max='!!Too long',
                            validate_len_min='!!Too short')
        gridEditor.numbertextbox(gridcell='qt')
        gridEditor.checkbox(gridcell='new')
        gridEditor.datetextbox(gridcell='date',format_date='short')
                        
    def inputgrid_struct(self,struct):
        r = struct.view().rows()
        r.cell('filter', name='FS',width='10em')
        r.cell('language', name='Lang',width='10em', dtype='T')
        r.cell('name', name='Name',width='10em', dtype='T')
        r.cell('qt', name='Qty',width='10em', dtype='R')
        r.cell('new', name='New',width='10em', dtype='B')
        r.cell('size', name='Size',width='10em', dtype='T')
        r.cell('date', name='Date',width='10em', dtype='D')
        
    def aux_test_1_grid_data(self):
        result = Bag()
        date = datetime.date.today()
        for i in range(100):
            pkey = 'r_%i' % i
            result[pkey] = Bag({'_pkey':pkey,'filter':'A','language':'Python','language_id':'6c75RL4uPJiMu5oEcfrx1w', 'name':'Dsc %i' % i, 'qt':None, 'new':bool(i%2), 'size':'big', 'date':date + datetime.timedelta(i)})
        return result
        
    def test_8_tree(self,pane):
        """Simple Drag"""
        root=pane.div(height='200px',overflow='auto')
        root.data('.tree.data',self.treedata())
        root.tree(storepath='.tree.data',node_droppable=True,
                                         node_draggable=True,
                                         drag_class='draggedItem',
                                         drop_action='alert(drop_data)')
        
    

        
    def treedata(self):
        b = Bag()
        b.setItem('person',None)
        b.setItem('person.name','John', job='superhero')
        b.setItem('person.age' , 22)
        b.setItem('person.sport.tennis' , 'good')
        b.setItem('person.sport.footbal' , 'poor')
        b.setItem('person.sport.golf' , 'medium')
        b.setItem('pet.animal', 'Dog',race='Doberman')
        return b