# -*- coding: UTF-8 -*-

# formEditor.py
# Created by Francesco Porcari on 2011-01-12.
# Copyright (c) 2011 Softwell. All rights reserved.

"""Form Handler tester"""

from gnr.web.gnrwebstruct import struct_method

class GnrCustomWebPage(object):
    dojo_source=True
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/formhandler:FormHandler"
         
    def _test_1_formPane_cp(self,pane):
        """Test form in contentPane form"""
        pane = pane.contentPane(height='150px')
        pane.formTester('form_cp')
    
    def test_2_formPane_tc(self,pane):
        """First test description"""
        tc = pane.tabContainer(height='250px',width='600px')
        t1 = tc.contentPane(title='Dummy')
        t2 = tc.contentPane(title='My Form').contentPane(_lazyBuild=True,detachable=True,height='100%',width='100%')
        t2.formTester('form_tc')
    
    def test_3_formPane_palette(self,pane):
        pane = pane.div(height='30px')
        pane.dock(id='test_3_dock')
        pane.palettePane('province',title='Province',dockTo='test_3_dock',_lazyBuild=True).formTester('form_palette')
        pane.palettePane('province_remote',title='Province Remote',dockTo='test_3_dock',
                         _lazyBuild='testPalette')

    
    def _test_5_formPane_palette_remote(self,pane):
        fb = pane.formbuilder(cols=4, border_spacing='2px')
        fb.dbselect(value="^.provincia",dbtable="glbl.provincia")
        fb.button('open',action="""var paletteCode='palette_'+pkey;
                                 var palette = genro.src.create('palettePane',{'paletteCode':paletteCode,
                                                                    title:'Palette:'+pkey,
                                                                    _lazyBuild:'testPalette',
                                                                    dockTo:'test_3_dock:open',
                                                                    remote_pkey:pkey},
                                                                    paletteCode);
                                    """,
                    pkey='=.provincia')
        
    def remote_testPalette(self,pane,pkey=None,**kwargs):
        pane.formTester('form_remote_%s' %pkey,hasSelector=False)
        pane.dataController("console.log('hei')",selfsubscribe_built=True)
            
    def _test_4_formPane_dialog(self,pane):
        pane.button('Show dialog',action='genro.wdgById("province_dlg").show()')
        dialog = pane.dialog(title='Province',nodeId='province_dlg',closable=True).contentPane(height='300px',width='400px',background_color='red',_lazyBuild=True)
        dialog.formTester('form_dialog')
    
    @struct_method
    def formTester(self,pane,formId=None,hasSelector=True):
        form = pane.formPane(formId=formId,datapath='.provincia')
        form.recordClusterStore('glbl.provincia')
        left = 'navigation,|,selectrecord,|,' if hasSelector else ''
        form.top.slotToolbar('prova','%s *,|,semaphore,|,formcommands,|,locker' %left)
        fb = form.content.formbuilder(cols=1, border_spacing='4px', width="300px", fld_width="100%")
        fb.field('sigla')
        fb.field('regione')
        fb.field('nome')
        fb.field('codice_istat')
        fb.field('ordine')
        fb.field('ordine_tot')
        fb.field('cap_valido')
        
        
                   
    @struct_method('prova_selectrecord')
    def prova_selectrecord(self,pane):
        pane.dbselect(value="^.prov",dbtable="glbl.provincia",parentForm=False,
                    validate_onAccept="this.form.publish('load',{destPkey:value});")
                    
    def rpc_salvaDati(self, dati, **kwargs):
        print "Dati salvati:"
        print dati
    
    @struct_method
    def recordClusterStore(self,pane,table=None,**kwargs):
        formAttr = pane.attributes
        for k,v in kwargs.items():
             formAttr['form_%s' %k] = v
        formAttr['form_table'] = table or self.maintable
        formAttr['form_loadmethod'] = 'loader_recordCluster'
        formAttr['form_savemethod'] = 'saver_recordCluster'
