# -*- coding: UTF-8 -*-

# formEditor.py
# Created by Francesco Porcari on 2011-01-12.
# Copyright (c) 2011 Softwell. All rights reserved.

"""Form Handler tester """

from gnr.web.gnrwebstruct import struct_method

class GnrCustomWebPage(object):
    dojo_source=True
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/formhandler:FormHandler"
    user_polling=0
    auto_polling=0

    
    @struct_method
    def formTester(self,pane,formId=None,startKey=None,**kwargs):
        form = pane.formPaneFrame(formId=formId,datapath='.provincia',**kwargs)
        form.recordClusterStore('glbl.provincia',storeType='Item',startKey=startKey,parentForm=formId)
        left = 'selectrecord,|,' if not startKey else ''
        form.slotToolbar('mytoolbar','%s *,|,semaphore,|,formcommands,|,locker' %left,toolbar_height='20px',side='top')
        fb = form.content.formbuilder(cols=2, border_spacing='4px', width="400px", fld_width="100%")
        fb.formContent()
        return form    
    
    @struct_method
    def formContent(self,fb):
        fb.field('sigla')
        fb.field('regione')
        fb.field('nome')
        fb.field('codice_istat')
        fb.field('ordine')
        fb.field('ordine_tot')
        fb.field('cap_valido')
        return fb
        
    def onLoading_glbl_provincia(self,record,newrecord,loadingParameters,recInfo):
        if record['sigla'] == 'AO':
            recInfo['_readonly'] = True
            
    def test_1_formPane_cp(self,pane):
        """Test form in contentPane form"""
        pane = pane.contentPane(height='180px',background='white')
        form = pane.formTester('form_cp')
        
    def _test_2_formPane_dbl_cp(self,pane):
        bc = pane.borderContainer(height='180px',background='white')
        formA = bc.contentPane(region='left',width='50%',datapath='.pane1',padding='5px').formTester('form_a',border='1px solid silver')
        formB = bc.contentPane(region='center',datapath='.pane2',padding='5px').formTester('form_b',border='1px solid silver')
    
    def _test_2_formPane_tc(self,pane):
        """First test description"""
        bc = pane.borderContainer(height='300px')
        topbc = bc.borderContainer(height='250px',region='top',splitter=True)
        bc.contentPane(region='center')
        tc = topbc.tabContainer(region='left',splitter=True,width='600px',nodeId='mytc')
        topbc.contentPane(region='center').div('pippo')
        t1 = tc.contentPane(title='Dummy',background_color='red')
        t2 = tc.contentPane(title='My Form').contentPane(detachable=True,_lazyBuild=True)
        t2.formTester('form_tc')
    
    def _test_3_formPane_palette(self,pane):
        pane = pane.div(height='30px')
        pane.dock(id='test_3_dock')
        pane.palettePane('province',title='Province',dockTo='test_3_dock',
                        _lazyBuild=True,width='600px',height='300px').formTester('form_palette')
        pane.palettePane('province_remote',title='Province Remote',dockTo='test_3_dock',
                         _lazyBuild='testPalette',width='600px',height='300px')

    
    def _test_5_formPane_palette_remote(self,pane):
        fb = pane.formbuilder(cols=4, border_spacing='2px')
        fb.dbselect(value="^.provincia",dbtable="glbl.provincia")
        fb.button('open',action="""var paletteCode='prov_'+pkey;
                                 var palette = genro.src.create('palettePane',{'paletteCode':paletteCode,
                                                                    title:'Palette:'+pkey,
                                                                    _lazyBuild:'testPalette',
                                                                    width:'600px',
                                                                    height:'300px',
                                                                    dockTo:false, //'test_3_dock:open',
                                                                    remote_pkey:pkey},
                                                                    paletteCode);
                                    """,
                    pkey='=.provincia')
        
    def remote_testPalette(self,pane,pkey=None,**kwargs):
        form = pane.formTester('formRemote_%s' %pkey,startKey=pkey)
        #form.dataController("this.form.publish('load',{destPkey:pkey});",pkey=pkey,selfsubscribe_built=True)
            
    def _test_4_formPane_dialog(self,pane):
        pane.button('Show dialog',action='genro.wdgById("province_dlg").show()')
        dialog = pane.dialog(title='Province',nodeId='province_dlg',closable=True).contentPane(height='300px',width='400px',background_color='red',_lazyBuild=True)
        dialog.formTester('form_dialog')
                   
    @struct_method('mytoolbar_selectrecord')
    def mytoolbar_selectrecord(self,pane,**kwargs):
        fb=pane.formbuilder(cols=1, border_spacing='0px',width='200px')
        fb.dbselect(value="^.prov",dbtable="glbl.provincia",parentForm=False,
                    validate_onAccept="this.form.publish('load',{destPkey:value});",lbl='Provincia',width='100%')
                    
    def rpc_salvaDati(self, dati, **kwargs):
        print "Dati salvati:"
        print dati
        
        
