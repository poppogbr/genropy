# -*- coding: UTF-8 -*-

# formEditor.py
# Created by Francesco Porcari on 2011-01-12.
# Copyright (c) 2011 Softwell. All rights reserved.

"""Form Handler tester """

from gnr.web.gnrwebstruct import struct_method

class GnrCustomWebPage(object):
    dojo_source=True
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/formhandler:FormHandler,foundation/includedview:IncludedView"
    user_polling=0
    auto_polling=0
    
    @struct_method
    def formTester(self,pane,frameCode=None,startKey=None,**kwargs):                
        form = pane.frameForm(frameCode=frameCode,rounded_bottom=10,table='glbl.provincia',
                            store='recordCluster',store_startKey=startKey or '*norecord*',**kwargs)
        form.testToolbar(startKey=startKey) 
        fb = form.formbuilder(cols=2, border_spacing='4px', width="400px",fld_width="100%")
        fb.formContent()
        return form
        
    @struct_method
    def testToolbar(self,form,startKey=None):
        left = 'selectrecord,|,' if not startKey else ''
        tb = form.top.slotToolbar('%s *,|,semaphore,|,formcommands,|,locker' %left,border_bottom='1px solid silver')
        if not startKey:
            fb = tb.selectrecord.formbuilder(cols=1, border_spacing='1px')
            fb.dbselect(value="^.prov",dbtable="glbl.provincia",parentForm=False,#default_value='MI',
                                        validate_onAccept="this.form.publish('load',{destPkey:value});",
                                        lbl='Provincia')
        return tb
        
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
    

    def test_0_frameform(self,pane):
        "Test FrameForm"
        form = pane.frameForm(frameCode='provincia_1',border='1px solid silver',datapath='.form',
                            rounded_bottom=10,height='180px',width='600px',center_widget='BorderContainer',
                            pkeyPath='.prov')
        form.testToolbar()
        store = form.formStore(storepath='.record',table='glbl.provincia',storeType='Item',
                               handler='recordCluster',startKey='*newrecord*',onSaved='reload')
        store.handler('load',_onCalling='console.log("xxxx")',default_ordine_tot='100')    
        form.contentPane(region='left',background='red',width='50px')
        form.contentPane(region='center').formbuilder(cols=2, border_spacing='3px').formContent()  
    
    
    def test_10_frameform_iv(self,pane):
        "Test FrameForm"
        form = pane.frameForm(frameCode='regione',border='1px solid silver',datapath='.form',
                            rounded_bottom=10,height='180px',width='600px',center_widget='TabContainer',
                            pkeyPath='.prov')
        form.testToolbar()
        store = form.formStore(storepath='.record',table='glbl.provincia',storeType='Item',
                               handler='recordCluster',startKey='*norecord*',onSaved='reload')
        store.handler('load',_onCalling='console.log("xxxx")',default_ordine_tot='100')    
        form.contentPane(title='Provincia').formbuilder(cols=2, border_spacing='3px').formContent()
        bc =form.borderContainer(title='Comuni')
        self.includedViewBox(bc,label='Comuni',datapath='comuni',
                             nodeId='comuni',table='glbl.localita',
                             struct='min',
                             reloader='^#regione_form.record.id', 
                             selectionPars=dict(where='$provincia=:provincia_id',
                             provincia_id='^#regione_form.record.sigla'))    
        
    def test_2_formPane_dbl_cp(self,pane):
        bc = pane.borderContainer(height='180px')
        bc.formTester(frameCode='form_a',region='left',datapath='.pane1',width='50%',border='1px solid gray',margin_right='5px')
        bc.formTester(frameCode='form_b',region='center',datapath='.pane2',border='1px solid gray')
    
    def test_2_formPane_tc(self,pane):
        """First test description"""
        bc = pane.borderContainer(height='300px')
        topbc = bc.borderContainer(height='250px',region='top',splitter=True)
        bc.contentPane(region='center')
        tc = topbc.tabContainer(region='left',splitter=True,width='600px',nodeId='mytc')
        topbc.contentPane(region='center').div('pippo')
        t1 = tc.contentPane(title='Dummy',background_color='red',onCreated='console.log("I was hoping")')
        t2 = tc.borderContainer(title='My Form',_lazyBuild=True)
        t2.formTester('form_tc',region='center')
        tc.contentPane(title='Third one')
    
    def test_3_formPane_palette(self,pane):
        pane = pane.div(height='30px')
        pane.dock(id='test_3_dock')
        pane.palettePane('province',title='Province',dockTo='test_3_dock',
                        width='600px',height='300px',_lazyBuild=True).formTester('form_palette')
        pane.palettePane('province_remote',title='Province Remote',dockTo='test_3_dock',
                        _lazyBuild='testPalette',width='600px',height='300px')

    
    def test_5_formPane_palette_remote(self,pane):
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
            
    def test_4_formPane_dialog(self,pane):
        pane.button('Show dialog',action='genro.wdgById("province_dlg").show()')
        dialog = pane.dialog(title='Province',nodeId='province_dlg',closable=True).contentPane(_lazyBuild=True)
        dialog.formTester('form_dialog',height='300px',width='500px')
                   
    @struct_method('mytoolbar_selectrecord')
    def mytoolbar_selectrecord(self,pane,**kwargs):
        fb=pane.formbuilder(cols=1, border_spacing='1px')
        fb.dbselect(value="^.prov",dbtable="glbl.provincia",parentForm=False,
                    validate_onAccept="this.form.publish('load',{destPkey:value});",lbl='Provincia')
                    
    def rpc_salvaDati(self, dati, **kwargs):
        print "Dati salvati:"
        print dati