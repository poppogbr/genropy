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


class SelectionHandler(BaseComponent):
    """
    To use it you should include  py_requires="selectionhandler"
    
    selectionHandler is a new component that is used as a replacement for includedView and recordDialog. 
    It adds a navigation toolbar for first, previous, next and last.
    It adds a + button to add new records from within the dialog
    It manages automatically:
    - all the dataControllers for add and delete .
    - the the add_action and del_action.
    - the connect_onRowDblClick parameter.
    
    To replace an includedView and recordDialog do the following:
    comment out:
        replace the call to includedView with a call to recordHandler
        #add_action
        #del_action
        #addOnCb
        #connect_onRowDblClick="FIRE .firedPkey = this.widget.rowIdByIndex($1.rowIndex);"
        #controllers that manage delete or add
        
    add a new parameter to replace the recordDialog function, having all parameters of the recordDialog
        passed into a dictionary, except for: onSaved='FIRE #contact_logGrid.reload;',
        dialogPars=dict(
    
    """
    py_requires='foundation/includedview:IncludedView,foundation/recorddialog'
    def selectionHandler(self,bc,nodeId=None,table=None,datapath=None,struct=None,label=None,
                         selectionPars=None,dialogPars=None,reloader=None,externalChanges=None,
                         hiddencolumns=None,custom_addCondition=None,custom_delCondition=None,
                         askBeforeDelete=True,checkMainRecord=True,onDeleting=None,dialogAddRecord=True,
                         onDeleted=None,groupingColumn=None,groups=None,add_enable=None,del_enable=None,
                         **kwargs):
        assert dialogPars,'dialogPars are Mandatory'
        assert not 'table' in dialogPars, 'take the table of the grid'
        assert not 'firedPkey' in dialogPars, 'auto firedPkey'
        assert not 'toolbarCb' in dialogPars,'toolbarCb calculated'
        assert not 'add_action' in kwargs, 'remove add_action par'
        assert 'order_by' in selectionPars, 'add order_by to selectionPars'
        assert not 'del_action' in kwargs,'remove del_action par'
        assert not 'connect_onRowDblClick' in kwargs,'remove connect_onRowDblClick par'
        
        dialogPars['table'] = table
        dlgId = dialogPars.get('dlgId',"%s_dlg" %nodeId)
        dialogPars['dlgId'] = dlgId
        dialogPars['formId'] = dialogPars.get('formId',"%s_form" %nodeId)
        dialogPars['datapath'] = dialogPars.get('datapath','#%s.dlg' %nodeId)
        dialogPars['onSaved'] = 'FIRE #%s.reload; %s' %(nodeId,dialogPars.get('onSaved',''))
        dialogPars['firedPkey'] = '^.pkey'
        dialogPars['add_action'] = dialogPars.get('add_action',True)
        dialogPars['lock_action'] = dialogPars.get('lock_action',True)
        dialogPars['toolbarCb'] = self._ivrd_toolbar

        self.recordDialog(**dialogPars)

        connect_onRowDblClick='FIRE .dlg.pkey = GET .selectedId;'
        self.includedViewBox(bc,label=label,datapath=datapath,
                             add_action='FIRE .dlg.pkey="*newrecord*";',
                             add_enable='^.can_add',del_enable='^.can_del',
                             del_action='FIRE .delete_record;',
                             nodeId=nodeId,table=table,struct=struct,hiddencolumns=hiddencolumns,
                             reloader=reloader, externalChanges=externalChanges,
                             connect_onRowDblClick=connect_onRowDblClick,
                             selectionPars=selectionPars,askBeforeDelete=True,**kwargs)
                             
        controller = bc.dataController(datapath=datapath)
        main_record_id = True
        if self.maintable and checkMainRecord:
            main_record_id='^form.record.%s' %self.db.table(self.maintable).pkey
        add_enable = add_enable or '^form.canWrite'
        del_enable = del_enable or '^form.canDelete'
        controller.dataFormula(".can_add","add_enable?(main_record_id!=null)&&custom_condition:false",
                              add_enable=add_enable,main_record_id=main_record_id,
                              custom_condition=custom_addCondition or True)
        controller.dataFormula(".can_del","del_enable?(main_record_id!=null)&&custom_condition:false",
                              del_enable=del_enable,selectedId='^.selectedId',_if='selectedId',_else='false',
                              main_record_id=main_record_id or True,custom_condition=custom_addCondition or True)
        controller.dataController("genro.dlg.ask(title, msg, null, '#%s.confirm_delete')" %nodeId,
                                    _fired="^.delete_record",title='!!Warning',
                                    msg='!!You cannot undo this operation. Do you want to proceed?',
                                    _if=askBeforeDelete)
        onDeleted = onDeleted or ''
        controller.dataRpc('.deletedPkey','iv_delete_selected_record',record_id='=.selectedId',table=table,
                            _confirmed='^.confirm_delete',_if='_confirmed=="confirm"',_onCalling=onDeleting,
                            _onResult='FIRE .afterDeleting; FIRE .reload; %s' %onDeleted)
        controller.dataController("""
                                 var form = genro.formById(gridId+'_form');
                                 if(!form.changed){
                                    FIRE .changeAnyway= btn;
                                 }else{
                                    var saveAction = "genro.fireEvent('#"+gridId+".saveAndChange','"+btn+"');";
                                    var noSaveAction = "genro.fireEvent('#"+gridId+".changeAnyway','"+btn+"');";
                                    genro.dlg.ask(title,msg,
                                                 {save:save,dont_save:dont_save,cancel:cancel},
                                                 {save:saveAction,dont_save:noSaveAction});
                                 }
                             
                              """, btn='^.navbutton', 
                                title='!!Warning',
                                msg='!!There are unsaved changes',
                                save='!!Save',save_act='FIRE .dlg.saveAndChangeIn',
                                dont_save='!!Do not save',
                                cancel='!!Cancel',gridId=nodeId)
        controller.dataController("""
                                    var btn = changeAnyway||saveAndChange;
                                    var grid = genro.wdgById(gridId);
                                    var rowcount = grid.rowCount;
                                    var newidx;
                                    if (btn == 'first' || btn=='new'){newidx = 0;} 
                                    else if (btn == 'last'){newidx = rowcount-1;}
                                    else if ((btn == 'prev') && (idx > 0)){newidx = idx-1;}
                                    else if ((btn == 'next') && (idx < rowcount-1)){newidx = idx+1;}
                                    SET .selectedIndex = newidx;
                                    var selectedId = btn=='new'?'*newrecord*':genro.wdgById(gridId).rowIdByIndex(newidx);
                                    if(changeAnyway){
                                        SET .dlg.current_pkey = selectedId;
                                        FIRE .dlg.load;
                                    }else if(saveAndChange){
                                        FIRE .dlg.saveAndChangeIn = selectedId;
                                    }
                                    """,saveAndChange="^.saveAndChange",
                                    changeAnyway='^.changeAnyway',gridId=nodeId,
                                    idx='=.selectedIndex')
        controller.data(".dialogAddDisabled", not dialogAddRecord)
        controller.dataFormula('.atBegin','(idx==0)',idx='^.selectedIndex')
        controller.dataFormula('.atEnd','(idx==genro.wdgById(gridId).rowCount-1)',idx='^.selectedIndex',gridId=nodeId)
                            
    def rpc_iv_delete_selected_record(self,record_id,table):
        tblobj = self.db.table(table)
        record = tblobj.record(pkey=record_id,for_update=True).output('dict')
        tblobj.delete(record)
        self.db.commit()
        return record_id
                             
    def _ivrd_toolbar(self,parentBC,add_action=None,lock_action=None,**kwargs):
        pane = parentBC.contentPane(padding='2px',overflow='hidden',**kwargs)
        tb = pane.toolbar(datapath='.#parent') #referred to the grid
        tb.button('!!First', fire_first='.navbutton', iconClass="tb_button icnNavFirst", disabled='^.atBegin', showLabel=False)
        tb.button('!!Previous', fire_prev='.navbutton', iconClass="tb_button icnNavPrev", disabled='^.atBegin', showLabel=False)
        tb.button('!!Next', fire_next='.navbutton', iconClass="tb_button icnNavNext", disabled='^.atEnd', showLabel=False)
        tb.button('!!Last', fire_last='.navbutton', iconClass="tb_button icnNavLast", disabled='^.atEnd', showLabel=False)
        if lock_action:
            spacer = tb.div(float='right',width='30px',height='20px',position='relative')
            spacer.button('!!Unlock', position='absolute',right='0px',fire='status.unlock', baseClass='no_background',
                        iconClass="tb_button icnBaseLocked", showLabel=False,hidden='^status.unlocked')
            spacer.button('!!Lock', position='absolute',right='0px',fire='status.lock',  baseClass='no_background',
                        iconClass="tb_button icnBaseUnlocked", showLabel=False,hidden='^status.locked')  
        if add_action:
            add_action = 'FIRE .navbutton="new";'
            add_class =  'buttonIcon icnBaseAdd'
            add_enable = '^form.canWrite'
            tb.button('!!Add', float='right',action=add_action,visible=add_enable,
                            iconClass=add_class, showLabel=False)
        
        

    