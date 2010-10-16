# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrlang import gnrImport,objectExtract

from gnr.core.gnrbag import Bag


class BatchMonitor(BaseComponent):
    js_requires = 'gnrcomponents/batch_handler/batch_handler'
    css_requires = 'gnrcomponents/batch_handler/batch_handler'
        
    def mainLeft_batch_monitor(self,tc):
        """!!Batch"""
        self.bm_monitor_pane(tc.contentPane(title='!!Batch',pageName='batch_monitor'))
    
    def bm_monitor_pane(self,pane):
        pane.dataController("batch_monitor.on_datachange(_triggerpars.kw);",_fired="^gnr.batch")
        #dovrei modificare il clieant in modo che mi prenda l elemento di classe bm_rootnode visibile
        # e gli appiccichi i termometri senza usare il node id
        pane.div(nodeId='bm_rootnode',_class='bm_rootnode')
        pane.dataRpc('dummy','setStoreSubscription',subscribe_batch_monitor_open=True,
                    storename='user',client_path='gnr.batch',active=True,
                    _onResult='genro.rpc.setPolling(1,1);')
        pane.dataRpc('dummy','setStoreSubscription',active=False,subscribe_batch_monitor_close=True,
                    _onCalling='genro.rpc.setPolling();',storename='user')
        
class TableScriptRunner(BaseComponent):
    py_requires='foundation/dialogs,gnrcomponents/printer_option_dialog'
    def onMain_table_script_runner(self):
        page = self.pageSource()
        plugin_main = page.div(datapath='gnr.plugin.table_script_runner',nodeId='table_script_runner')
        plugin_main.dataController(""" var params = table_script_run[0];
                                       SET .res_type= params['res_type'];
                                       SET .table =  params['table'];
                                       SET .resource =  params['resource'];
                                       SET .structpath =  params['structpath'];
                                       SET .selectionName =  params['selectionName'];
                                       SET .selectedRowidx =  params['selectedRowidx'];
                                       SET .paramspath = params['paramspath'];
                                       FIRE .build_pars_dialog;
                                       FIRE #table_script_dlg_parameters.open;
                                    """,subscribe_table_script_run=True)
                                    
        plugin_main.dataRpc('dummy','table_script_run',
                _fired='^.run',
                _onCalling='PUBLISH batch_monitor_open;',
                parameters='=.parameters',resource='=.resource',
                res_type='=.res_type',
                table='=.table',
                selectionName='=.selectionName',
                struct='==this.getRelativeData(_structpath);',
                _structpath='=.structpath',
                otherParams='==this.getRelativeData(_paramspath)',
                _paramspath='=.paramspath',
                selectedRowidx="=.selectedRowidx")
                
        plugin_main.div().remote('table_script_parameters',
                            resource='=.resource',
                            res_type='=.res_type',
                            title='=.title',
                            table='=.table',
                            _fired='^.build_pars_dialog')
                            
    def table_script_resource_tree(self,pane,table=None,res_type=None,selectionName=None,gridId=None,_class=None,**kwargs):
        pane.dataRemote('.tree.store', 'table_script_resource_tree_data', table=table, cacheTime=10,res_type=res_type)
        pane.tree(storepath='.tree.store', persist=False, 
                          labelAttribute='caption',hideValues=True,
                          _class=_class,
                          selected_resource ='.resource',
                          connect_ondblclick='FIRE .run_table_script',
                          tooltip_callback="return sourceNode.attr.description || sourceNode.label;",
                          **kwargs) 
                          
        pane.dataController("""
                            var selectedRowidx = gridId?genro.wdgById(gridId).getSelectedRowidx():null;
                            PUBLISH table_script_run={table:table,res_type:res_type,selectionName:selectionName,selectedRowidx:selectedRowidx,resource:resource};""",
                            _fired="^.run_table_script",selectionName=selectionName,table=table,
                            gridId=gridId,res_type=res_type,resource='=.resource')

    def remote_table_script_parameters(self,pane,table=None,res_type=None,resource='',title=None,**kwargs):
        pkgname,tblname = table.split('.')
        if not resource:
            return
        resource = resource.replace('.py','')
        cl=self.site.loadResource(pkgname,'tables',tblname,res_type,"%s:Main" %resource) #faccio mixin con prefisso
        self.mixin(cl,methods='table_script_*,rpc_table_script_*')
        batch_dict = objectExtract(cl,'batch_') 
        batch_dict['resource_name'] = resource
        batch_dict['res_type'] = res_type
        pane.data('.batch',batch_dict)
        dlg_dict = objectExtract(cl,'dialog_')
        dlg_dict['title'] = dlg_dict.get('title',batch_dict.get('title'))
        pane.data('.dialog',dlg_dict)
        def cb_center(parentBc,**kwargs):
            if hasattr(self,'table_script_option_pane'):
                center = parentBc.tabContainer(datapath='.data',**kwargs)
                self.table_script_parameters_pane(center.contentPane(title='!!Parameters'))
                self.table_script_option_pane(center.contentPane(title='!!Options',datapath='.batch_options'))
            else:
                center = parentBc.contentPane(datapath='.data',**kwargs)
                self.table_script_parameters_pane(center)
        
        dlg = self.simpleDialog(pane,datapath='.dialog',title='^.title',height='^.height',width='^.width',
                             cb_center=cb_center,dlgId='table_script_dlg_parameters')
                         
        dlg.dataController("""FIRE .close;
                            SET #table_script_runner.parameters=pars;
                            FIRE #table_script_runner.run;""",
                            _fired="^.save",pars='=.data')
                     
    def rpc_table_script_run(self,table=None,resource=None,res_type=None,selectionName=None,selectedRowidx=None,**kwargs):
        tblobj = self.tblobj or self.db.table(table)
        res_obj=self.site.loadTableScript(self,tblobj,'%s/%s' %(res_type,resource),class_name='Main')
        res_obj.defineSelection(selectionName=selectionName,selectedRowidx=selectedRowidx)
        res_obj(**kwargs)
        
    def rpc_table_script_resource_tree_data(self,table=None,res_type=None):
        pkg,tblname = table.split('.')
        result = Bag()
        resources = self.site.resource_loader.resourcesAtPath(pkg,'tables/%s/%s' %(tblname,res_type),'py')
        forbiddenNodes = []
        def cb(node,_pathlist=None):
            has_parameters = False
            if node.attr['file_ext'] == 'py':
                resmodule = gnrImport(node.attr['abs_path'])
                tags = getattr(resmodule,'tags','') 
                
                if tags and not self.application.checkResourcePermission(tags, self.userTags):
                    if node.label=='_doc':
                        forbiddenNodes.append('.'.join(_pathlist))
                    return
                caption = getattr(resmodule,'caption',node.label)
                description = getattr(resmodule,'description','')
                if  node.label=='_doc':
                    result.setAttr('.'.join(_pathlist),dict(caption=caption,description=description,tags=tags,
                                                            has_parameters=has_parameters))
                else:
                    mainclass = getattr(resmodule,'Main',None)
                    assert mainclass,'Main class is mandatory in tablescript resource'
                    has_parameters = hasattr(mainclass,'parameters_pane')
                    result.setItem('.'.join(_pathlist+[node.label]),None,caption=caption,description=description,
                                    resource=node.attr['rel_path'][:-3],has_parameters=has_parameters)            
        resources.walk(cb,_pathlist=[])
        for forbidden in forbiddenNodes:
            result.pop(forbidden)
        return result