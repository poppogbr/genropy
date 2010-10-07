# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag,BagResolver

def _getTreeRowCaption(tblobj):
    if hasattr(tblobj,'treeRowCaption'):
        return tblobj.treeRowCaption()
    return  '$child_code,$description:%s - %s'

def _getTreeRowCaption2(tblobj):
    if hasattr(tblobj,'treeRowCaption'):
        return tblobj.treeRowCaption()
    return  '$child_code'

class HTableResolver(BagResolver):
    classKwargs={'cacheTime':300,
                 'readOnly':False,
                 'table':None,
                 'rootpath':None,
                 '_page':None}
    classArgs=['table','rootpath']
            
    def load(self):
        db= self._page.db
        tblobj = db.table(self.table) 
        rows = tblobj.query(columns='*,$child_count,$hdescription',where="COALESCE($parent_code,'')=:rootpath" ,
                     rootpath=self.rootpath or '',order_by='$child_code').fetch()
        children = Bag()
        for row in rows:
            child_count= row['child_count']
            value=HTableResolver(table=self.table,rootpath=row['code'],child_count=child_count,_page=self._page) if child_count else None
            description = row['description']
            if description:
                get_tree_row_caption = _getTreeRowCaption
            else:
                get_tree_row_caption = _getTreeRowCaption2
            children.setItem(row['child_code'], value,
                             caption=tblobj.recordCaption(row,rowcaption=get_tree_row_caption(tblobj)),
                             _pkey=row['pkey'],code=row['code'],child_count=child_count,checked=False,
                             parent_code=row['parent_code'],hdescription=row['hdescription'])#_attributes=dict(row),
        return children
        
    def resolverSerialize(self):
        self._initKwargs.pop('_page')
        return BagResolver.resolverSerialize(self)
        
class HTableHandlerBase(BaseComponent):
    
    def ht_treeDataStore(self,table=None,rootpath=None,rootcaption=None):
        tblobj= self.db.table(table)
        result = Bag()
        if rootpath:
            row=tblobj.query(columns='*',where='$code=:code',code=rootpath).fetch()[0]
            description = row['description']
            if description:
                get_tree_row_caption = _getTreeRowCaption
            else:
                get_tree_row_caption = _getTreeRowCaption2
            caption=tblobj.recordCaption(row,rowcaption=get_tree_row_caption(tblobj))
            rootlabel = row['child_code']
            pkey=row['pkey']
            _attributes=dict(row)
            rootpath=row['code']
            code=row['code']
            child_count = row['child_count']

        else:
            caption=rootcaption
            rootlabel ='_root_'
            _attributes=dict()
            pkey=None
            code=None
            rootpath=None
            child_count = tblobj.query().count()
        value =  HTableResolver(table=table,rootpath=rootpath,_page=self) if child_count else None
        result.setItem(rootlabel,value,child_count=child_count, caption=caption,_pkey=pkey,code=code,checked=False)#,_attributes=_attributes)
        return result
                    
class HTableHandler(HTableHandlerBase):
    css_requires='public'
    def htableHandler(self,parent,nodeId=None,datapath=None,table=None,rootpath=None,label=None,
                    editMode='bc',childTypes=None,dialogPars=None,loadKwargs=None,parentLock=None,where=None,onChecked=None):
        """
        .tree: tree data:
                        store
                        **selected elements
        .edit (sym #nodeId_edit): pane data: **controllers
                                       form
                                       record
        formId:nodeId_form 
        controllerNodeId:nodeId_edit
        treeId:nodeId_tree
        editMode:'bc','sc','dlg'
        """
        disabled ='^#%s.edit.status.locked'%nodeId
        if parentLock:
            parent.dataController("SET .edit.status.locked=parentLock;",parentLock=parentLock,datapath=datapath)
            parent.dataController("""SET %s=isLocked;""" %parentLock[1:],
                                    parentLock=parentLock,isLocked='^.edit.status.locked',
                                    _if='parentLock!=isLocked',datapath=datapath)
                                        
        formPanePars = dict(selectedPage='^.edit.selectedPage',_class='pbl_roundedGroup')
        if editMode=='bc':
            bc = parent.borderContainer(region='center',datapath=datapath,nodeId=nodeId,margin='2px')
            treepane = bc.borderContainer(region='left',width='40%',splitter=True,_class='pbl_roundedGroup')
            formPanePars['region'] = 'center'            
            formBC = bc.borderContainer(region='center')
            
        elif editMode=='sc':
            sc = parent.stackContainer(region='center',datapath=datapath,nodeId=nodeId,
                                        selectedPage='^.selectedPage',margin='2px')
            treepane = sc.borderContainer(pageName='tree',_class='pbl_roundedGroup')
            formPanePars['pageName'] = 'edit'
            formBC = sc.borderContainer(region='center')
            
        elif editMode=='dlg':
            assert dialogPars,'for editMode == "dlg" dialogPars are mandatory'
            treepane = parent.borderContainer(region='center',datapath=datapath,nodeId=nodeId,margin='2px',_class='pbl_roundedGroup')
            formBC = self.simpleDialog(treepane,dlgId='%s_dlg' %nodeId,**dialogPars)
            formPanePars['region'] = 'center'
            
        recordlabel = formBC.contentPane(region='top',_class='pbl_roundedGroupLabel')
        recordlabel.div('^.edit.record?caption')
        footer = formBC.contentPane(region='bottom',_class='pbl_roundedGroupBottom')
        if editMode=='dlg':
            footer.button('!!Close',fire='.close')

        formpane = formBC.stackContainer(pageName='edit',**formPanePars)
        footer.dataController("""
                            var pathlist = currpath.split('.');
                            var rootnode = genro.nodeById(labelNodeId).clearValue().freeze();
                            var label,path2set;
                            for(var i=0;i<pathlist.length-1;i++){
                                label = pathlist[i];
                                path2set = path2set?path2set+'.'+label:label;
                                var action = "this.setRelativeData('.tree.path','"+path2set+"');";
                                var showLabel = true;
                                if(label=='_root_'){
                                    label = rootName;
                                }else{
                                    label = label;
                                }
                                rootnode._('button',{label:label,action:action,'float':'left',font_size:'.9em',
                                                    iconClass:'breadcrumbIcn',showLabel:showLabel});
                                    
                            }
                            rootnode.unfreeze();

                            """,
                             currpath='=.tree.path',_fired='^.edit.record.code',
                             labelNodeId='%s_nav' %nodeId,rootName='!!Root:')
        
        self.ht_tree(treepane,table=table,nodeId=nodeId,disabled=disabled,
                    rootpath=rootpath,childTypes=childTypes,editMode=editMode,label=label,onChecked=onChecked)
        self.ht_edit(formpane,table=table,nodeId=nodeId,disabled=disabled,
                        rootpath=rootpath,editMode=editMode,loadKwargs=loadKwargs)
                        
    def ht_edit_dlg_bottom(self,bc,**kwargs):
        bottom = bc.contentPane(**kwargs)
        bottom.button('!!Close',fire='.close')
                
    def ht_edit(self,sc,table=None,nodeId=None,disabled=None,rootpath=None,editMode=None,loadKwargs=None):
        formId='%s_form' %nodeId
        norecord = sc.contentPane(pageName='no_record').div('No record selected')
        bc = sc.borderContainer(pageName='record_selected')
        toolbar = bc.contentPane(region='top',overflow='hidden').toolbar(_class='standard_toolbar')
        toolbar.dataFormula('.edit.status.locked',True,_onStart=True)
        toolbar.dataController("""
                            if(isLocked){
                            //if not unlockable return
                                isLocked = isLocked //if unlocable 
                            }
                            SET .edit.status.locked=!isLocked
                            """,
                            _fired='^.edit.status.changelock',
                            isLocked='=.edit.status.locked')
        toolbar.dataController("""
                             SET .edit.status.statusClass = isLocked?'tb_button icnBaseLocked':'tb_button icnBaseUnlocked';
                             SET .edit.status.lockLabel = isLocked?unlockLabel:lockLabel;
                               """,isLocked="^.edit.status.locked",lockLabel='!!Lock',
                                unlockLabel='!!Unlock')
        
        
        
        self.ht_edit_toolbar(toolbar,nodeId=nodeId,disabled=disabled,editMode=None)
        bc.dataController("SET .edit.selectedPage=pkey?'record_selected':'no_record'",pkey="^.tree.pkey")
        bc.dataController("""
                            var destPkey = selPkey;
                            var cancelCb = function(){
                                genro.setData('#%s.tree.pkey',currPkey);
                                genro.setData('#%s.tree.path',rootpath?currPkey.slice(rootpath.length-1):currPkey);
                                };
                            genro.formById(formId).load({destPkey:destPkey,cancelCb:cancelCb});
                                """ %(nodeId,nodeId),rootpath='=.tree.store?rootpath',
                            selPkey='^.tree.pkey',currPkey='=.edit.pkey',_if='selPkey!=currPkey',
                            formId=formId)

        bc.dataController("""
                             var rootpath = rootpath || null;
                             
                             if (destPkey!='*newrecord*'){
                                 var editNode = treestore.getNode(treepath);
                                 var attr= editNode.attr;
                                 attr.caption = treeCaption;
                                 editNode.setAttr(attr);
                                 FIRE .edit.load;
                             }else{
                                SET .edit.pkey = savedPkey;
                                FIRE .edit.load;
                                var parentPath = rootpath?parent_code.slice(rootpath.length):parent_code?'_root_.'+parent_code:'_root_'
                                var refreshFromNode = treestore.getNode(parentPath);
                                
                                if(!refreshFromNode.getValue()){
                                    refreshFromNode = refreshFromNode.getParentNode();
                                }
                                refreshFromNode.refresh(true);
                             }
                         """,
                        _fired="^.edit.onSaved",destPkey='=.tree.pkey',parent_code='=.edit.record.parent_code',
                        savedPkey='=.edit.savedPkey',rootpath='=.tree.store?rootpath',
                        treepath='=.tree.path',treestore='=.tree.store',
                        treeCaption='=.edit.savedPkey?caption')
        bc.dataController("""
                            if (rootpath){
                                path=code.slice(rootpath.length);
                            }else{
                                path = code?'_root_.'+code:'_root_';
                            }
                            SET .tree.path=path;""",code="^.edit.record.code",
                            rootpath='=.tree.store?rootpath',_if='code')
        
        
        bc.dataRpc('.edit.del_result','deleteDbRow',pkey='=.edit.pkey',
                    _POST=True,table=table,_delStatus='^.edit.delete',
                    _if='_delStatus=="confirm"',_else='genro.dlg.ask(title,msg,null,"#%s.edit.delete")' %nodeId,
                    title='!!Deleting record',msg='!!You cannot undo this operation. Do you want to proceed?',
                    _onResult="""var path = $2.currpath.split('.');
                                 path.pop();
                                 var path = path.join('.');
                                 $2.treestore.getNode(path).refresh(true)
                                 SET .tree.path = path;""",currpath='=.tree.path',treestore='=.tree.store')
                    
        getattr(self,formId)(bc,region='center',table=table,
                              datapath='.edit.record',controllerPath='#%s.edit.form' %nodeId,
                              formId=formId,
                              disabled= disabled,
                              pkeyPath='#%s.edit.pkey' %nodeId)
        tblobj = self.db.table(table)
        loadKwargs =  loadKwargs or dict()
       
        loadKwargs['default_parent_code'] = '=.defaults.parent_code'                                
        self.formLoader(formId,datapath='#%s.edit' %nodeId,resultPath='.record',_fired='^.load',
                        table=table, pkey='=.pkey',**loadKwargs)
        self.formSaver(formId,datapath='#%s.edit' %nodeId,resultPath='.savedPkey',_fired='^.save',
                        table=table,onSaved='FIRE .onSaved;',#onSaving='if($1.getItem("child_code").indexOf(".")>=0){}',
                        rowcaption=_getTreeRowCaption(self.db.table(table)))

    def ht_edit_toolbar(self,toolbar,nodeId=None,disabled=None,editMode=None):
        nav = toolbar.div(float='left',nodeId='%s_nav' %nodeId)
        spacer = toolbar.div(float='right',_class='button_placeholder')
        spacer.button(label='^.edit.status.lockLabel', fire='.edit.status.changelock',
                      iconClass="^.edit.status.statusClass",showLabel=False)
        spacer = toolbar.div(float='right',_class='button_placeholder')
        spacer.dataController("""genro.dom.removeClass(semaphoreId,"greenLight redLight yellowLight");
              if(isValid){
                 if(isChanged){
                     genro.dom.addClass(semaphoreId,"yellowLight");
                 }else{
                     genro.dom.addClass(semaphoreId,"greenLight");
                 }
              }else{
                    genro.dom.addClass(semaphoreId,"redLight");
              }
              """,isChanged="^.edit.form.changed",semaphoreId='%s_semaphore' %nodeId,
            isValid='^.edit.form.valid')
        spacer.div(nodeId='%s_semaphore' %nodeId,_class='semaphore',margin_top='3px',
                  hidden=disabled)  
        toolbar.button('!!Save',fire=".edit.save", float='right',
                        iconClass="tb_button db_save",showLabel=False,
                        hidden=disabled)
        toolbar.button('!!Revert',fire=".edit.load", iconClass="tb_button db_revert",float='right',
                        showLabel=False,hidden=disabled)      
        toolbar.button('!!Add',action="""   SET .edit.defaults.parent_code = GET .edit.record.parent_code;
                                            SET .tree.pkey = '*newrecord*';
                                            """,iconClass='db_add tb_button',
                                            showLabel=False,hidden=disabled,float='right')
        toolbar.button('!!Delete',fire=".edit.delete",iconClass='db_del tb_button',
                                            showLabel=False,hidden=disabled,
                                            visible='^.edit.enableDelete',
                                            float='right')
        toolbar.dataFormula('.edit.enableDelete','child_count==0',child_count='^.tree.child_count')
        if editMode=='sc':
            toolbar.button('!!Tree',action="SET .selectedPage = 'tree';")
                                            
                                                                 
    def ht_tree(self,bc,table=None,nodeId=None,rootpath=None,disabled=None,childTypes=None,editMode=None,label=None,onChecked=None):
        
        labelbox = bc.contentPane(region='top',_class='pbl_roundedGroupLabel')
        labelbox.div(label,float='left')
        add_action="""SET .edit.defaults.parent_code = GET .tree.code;
                      SET .tree.pkey = '*newrecord*';"""
        if editMode=='dlg':
            add_action = '%s FIRE #%s_dlg.open;' %(add_action,nodeId)
        btn_addChild = labelbox.div(float='right', _class='buttonIcon icnBaseAdd',connect_onclick=add_action,
                        margin_right='2px',visible='^.tree.path',default_visible=False)
        if childTypes:
            childTypesMenu = Bag()
            for k,v in childTypes.items():
                childTypesMenu.setItem(k,None,caption=v,action="SET .edit.childType = $1.fullpath; %s" %add_action)
            labelbox.data('.childTypesMenu',childTypesMenu)
            btn_addChild.menu(storepath='.childTypesMenu',modifiers='*',_class='smallmenu')            
        tblobj = self.db.table(table)
        center = bc.contentPane(region='center')
        center.data('.tree.store',self.ht_treeDataStore(table=table,rootpath=rootpath,rootcaption=tblobj.name_plural),
                    rootpath=rootpath)
                    
        connect_ondblclick=None
        if editMode=='sc':
            connect_ondblclick = 'SET .selectedPage = "edit";'
        elif editMode=='dlg':
            connect_ondblclick = 'FIRE #%s_dlg.open;' %nodeId
        center.tree(storepath ='.tree.store',
                    isTree =False,hideValues=True,
                    inspect ='shift',labelAttribute ='caption',
                    selected_pkey='.tree.pkey',selectedPath='.tree.path',  
                    selectedLabelClass='selectedTreeNode',
                    selected_code='.tree.code',
                    selected_child_count='.tree.child_count',
                    connect_ondblclick=connect_ondblclick,
                    onChecked=onChecked)
        
class HTablePicker(HTableHandlerBase):
    py_requires='foundation/dialogs,foundation/includedview:IncludedView'
    
    def htablePicker(self,parent,table=None,rootpath=None,
                    input_codes=None,
                    output_codes=None,
                    output_pkeys=None,
                    nodeId=None,datapath=None,dialogPars=None,
                    caption=None,grid_struct=None,grid_columns=None,
                    condition=None,condition_pars=None,**kwargs):
        
        self._htablePicker_main(parent,table=table,rootpath=rootpath,
                                input_codes=input_codes,output_codes=output_codes,
                                output_pkeys=output_pkeys,
                                nodeId=nodeId,
                                datapath=datapath,dialogPars=dialogPars,grid_struct=grid_struct,
                                grid_columns=grid_columns,
                                condition=condition,condition_pars=condition_pars)
    
    
    def htablePickerOnRelated(self,parent,table=None,rootpath=None,
                            input_pkeys=None,output_pkeys=None,
                            related_table=None,relation_path=None,
                            nodeId=None,datapath=None,dialogPars=None,
                            caption=None,grid_struct=None,grid_columns=None,
                            condition=None,condition_pars=None,**kwargs):
            
        self._htablePicker_main(parent,table=table,rootpath=rootpath,
                        related_table=related_table,
                        relation_path=relation_path,
                        input_pkeys=input_pkeys or '',output_pkeys=output_pkeys,nodeId=nodeId,
                        datapath=datapath,dialogPars=dialogPars,grid_struct=grid_struct,grid_columns=grid_columns,
                        condition=condition,condition_pars=condition_pars)
    
    
    def _htablePicker_main(self,parent,table=None,rootpath=None,
                    input_pkeys=None,
                    input_codes=None,
                    output_pkeys=None,
                    output_codes=None,
                    nodeId=None,datapath=None,dialogPars=None,
                    caption=None,grid_struct=None,grid_columns=None,
                    condition=None,
                    condition_pars=None,
                    related_table=None,
                    relation_path=None,
                    **kwargs):
        """params htable:
            parent
            column??
            resultpath
            """
        grid_where = '$code IN :codes'
        if related_table:
            grid_where = '%s IN :codes' %relation_path 
        if condition:
            grid_where = '%s AND %s' %(grid_where,condition)
        condition_pars = condition_pars or dict()
        dialogPars = dialogPars or dict()
        tblobj = self.db.table(table)
        dialogPars['title'] = dialogPars.get('title','%s picker' %tblobj.name_long)
        dialogPars['height'] = dialogPars.get('height','300px')
        dialogPars['width'] =  dialogPars.get('width', '450px')
        
        dlgbc = self.formDialog(parent,datapath=datapath,formId=nodeId,
                                cb_center=self.ht_pk_center,caption=caption,table=table,
                                grid_struct=grid_struct,grid_columns=grid_columns,
                                grid_where=grid_where,condition_pars=condition_pars,
                                output_codes=output_codes,output_pkeys=output_pkeys,
                                related_table=related_table,**dialogPars)
        dlgbc.dataController("FIRE .open;",**{"subscribe_%s_open" %nodeId:True})
        
                                                                
        dlgbc.dataRpc('.data.tree','ht_pk_getTreeData',table=table,
                        rootpath=rootpath,rootcaption=tblobj.name_plural,
                        input_pkeys=input_pkeys,input_codes=input_codes,
                        relation_path=relation_path,related_table=related_table,
                        nodeId='%s_loader' %nodeId,
                        _onResult="""FIRE .reload_tree;
                                     PUBLISH %s_tree_checked; 
                                     FIRE .loaded;""" %nodeId)
        dlgbc.dataController("PUBLISH %s_confirmed; FIRE .saved;" %nodeId,
                            nodeId="%s_saver" %nodeId)

  
    def rpc_ht_pk_getTreeData(self,table=None,rootpath=None,rootcaption=None,
                             input_codes=None,input_pkeys=None,related_table=None,
                             relation_path=None):
        result = self.ht_treeDataStore(table=table,rootpath=rootpath,rootcaption=rootcaption)
        htableobj = self.db.table(table)
        if related_table:
            if isinstance(input_pkeys,basestring):
                input_pkeys = input_pkeys.split(',')
            reltableobj = self.db.table(related_table)
            input_codes = reltableobj.query(columns='%s AS hcode' %relation_path,where='$%s IN :pkeys' %reltableobj.pkey,
                                            pkeys=input_pkeys,distinct=True,addPkeyColumn=False).fetch()
            input_codes = [r['hcode'] for r in input_codes]
        if input_codes:
            if isinstance(input_codes,basestring):
                input_codes = input_codes.split(',')
            for code in input_codes:
                node = result.getNode('#0.%s' %code)
                if node and not node.attr['child_count']>0:
                    node.setAttr(checked=True)
            self._ht_pk_setParentStatus(result)
        return result
        
    def _ht_pk_setParentStatus(self,bag):
        for node in bag.nodes:        
            value = node.getValue('static')
            if isinstance(value,Bag):
                self._ht_pk_setParentStatus(value)
                checked_elements = value.digest('#a.checked')
                n_checked = checked_elements.count(True)
                n_fuzzy = checked_elements.count(-1)
                if n_checked == len(value):
                    checked = True
                elif n_checked==0 and n_fuzzy==0:
                    checked = False
                else:
                    checked = -1
                node.attr['checked'] = checked
        
    
    def ht_pk_center(self,parentBC,table=None,formId=None,datapath=None,
                    controllerPath=None,region=None,caption=None,grid_struct=None,grid_columns=None,
                    related_table=None,grid_where=None,condition_pars=None,output_codes=None,output_pkeys=None,**kwargs):
        bc = parentBC.borderContainer(_class='pbl_roundedGroup',region=region)
        
        self._ht_pk_tree(bc.borderContainer(region='left',width='150px',splitter=True),
                         caption=caption,datapath=datapath,
                        controllerPath=controllerPath,
                        formDatapath='.data.checked_codes',formId=formId,
                        output_codes=output_codes,output_pkeys=output_pkeys)
        self._ht_pk_view(bc.borderContainer(region='center'),
                        caption=caption, gridId='%s_grid' %formId,
                        table=table,related_table=related_table,grid_where=grid_where,condition_pars=condition_pars,
                        output_pkeys=output_pkeys,grid_struct=grid_struct,
                        grid_columns=grid_columns)

    def _ht_pk_tree(self,bc,caption=None,datapath=None,formId=None,
                    controllerPath=None,output_codes=None,
                    output_pkeys=None,**kwargs):
        #top = bc.contentPane(region='top').div(value=caption,height='20px')
        treeId = '%s_tree' %formId
        center = bc.contentPane(region='center',datapath=datapath,formId=formId,controllerPath=controllerPath)
        center.tree(storepath ='.tree._root_',
                    isTree =False,hideValues=True,
                    _fired='^.#parent.reload_tree',
                    nodeId=treeId,eagerCheck=True,
                    inspect ='shift',labelAttribute ='caption',onChecked=True)
                    
                    
        bc.dataController("""

                            var result_codes = [];
                            var result_pkeys = [];
                            treedata.walk(function(n){
                                if (n.attr['checked']==true && !n.getValue()){
                                    result_codes.push(n.attr['code']);
                                    result_pkeys.push(n.attr['_pkey']);
                                }
                            },'static');
                            SET .data.checked_codes = result_codes;
                            SET .data.checked_pkeys = result_pkeys;
                            if(output_codes){
                                this.setRelativeData(output_codes,result_codes.join(','));
                            }
                            if(output_pkeys){
                                this.setRelativeData(output_pkeys,result_pkeys.join(','));
                            }
                            
                            FIRE .preview_grid.load;
                            """ ,output_codes = output_codes or False,
                            output_pkeys= output_pkeys or False,
                            treedata='=.data.tree',
                            **{'subscribe_%s_checked' %treeId:True})
                            
                            
                    
    def _ht_pk_view(self,bc,caption=None,gridId=None,table=None,grid_columns=None,
                    grid_struct=None,grid_where=None,condition_pars=None,related_table=None,
                    output_pkeys=None,**kwargs):
                    
        self.includedViewBox(bc,label=False,datapath='.preview_grid',
                             nodeId=gridId,columns=grid_columns,
                             table=related_table or table,
                             struct=grid_struct,
                             reloader='^.load', addCheckBoxColumn=bool(related_table),
                             selectionPars=dict(where=grid_where,
                                                codes='=.#parent.data.checked_codes',
                                                _delay=1000,
                                                _onResult="""
                                                    var bag =result.getValue();
                                                    bag.forEach(function(n){
                                                        var old_n = old.getNodeByAttr('_pkey',n.attr._pkey);
                                                        n.attr._checked=(old_n && old_n.attr._checked==false)?false:true;
                                                    },'static');     
                                                """),**condition_pars)
        #bc.dataController("""
        #                    console.log('eseguo');
        #                    var output_pkey_list = [];
        #                    selection.forEach(function(n){
        #                        if(n.attr._checked==true){
        #                            output_pkey_list.push(n.attr._pkey);
        #                        }
        #                    });
        #                    this.setRelativeData(output_pkeys,output_pkey_list.join(','));
        #                    """ ,
        #                    output_pkeys=output_pkeys,
        #                    selection="^.preview_grid.selection",_if='selection')
        #                                    
        #                                        
        
        
        

