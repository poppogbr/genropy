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
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrbag import Bag

class TableHandlerForm(BaseComponent):
    def pageList(self, pane):
        self.query_helper_main(pane)
        filterpath = 'filter.%s' % self.pagename
        if not filterpath in self.clientContext:
            filterBase = self.filterBase()
            if filterBase:
                cookie = self.clientContext
                cookie[filterpath] = filterBase
                self.clientContext = cookie
                #pane.data('_clientCtx.%s'%filterpath, filterBase)
        pane.data('list.showToolbox', False)
        pane.data('list.showExtendedQuery', False)
        pane.dataController("""genro.wdgById("gridbc").showHideRegion("top",showquery);genro.resizeAll();""",
                            showquery='^list.showExtendedQuery',
                            _fired='^gnr.onStart')
        pane.dataController("""if(page=='view'){SET list.selectedTop=1;}
                                   else if(page=='query'){SET list.selectedTop=0;}
                                """, page='^list.toolboxSelected')

        pane.dataController("""genro.wdgById("gridbc").showHideRegion("left",show);
                                genro.resizeAll();
                               genro.publish('main_left_set_status',!show);
                               """,
                            show='^list.showToolbox', _fired='^gnr.onStart')
        pane.dataFormula('list.showExtendedQuery', "true", _if='where.len()>1', where='^list.query.where')
        self.pageListController(pane)

        thframe = pane.framePane(frameCode='mainlist',datapath='list')
        self.listController(thframe)
        self.listToolbar(thframe.top)
        bc = thframe.center.borderContainer(design='sidebar', nodeId='gridbc')
        self.lstToolbox(bc.borderContainer(width='250px', region='left', _class='toolbox', splitter=True, hidden=True))
        self.lstEditors_main(bc.stackContainer(region='top', height='20%', splitter=True, hidden=True, selected='^list.selectedTop'))
        self.listBottomPane(bc, region='bottom')
        st = bc.stackContainer(region='center', datapath='list.grid', margin='0px',
                              nodeId='_gridpane_', selected='^list.gridpage')
        self.gridPane(st)
        st.contentPane().div(_class='waiting')



    def listViewStructures(self, pane):
        """Prepare databag for"""
        structures = Bag()

        def setInStructureCb(label, handler):
            structures.setItem(label, handler(self.newGridStruct(maintable=self.maintable)), objtype='view', tbl=self.maintable)

        viewMenu = self.listCustomCbBag('lstBase_', 'lstBase', cb=setInStructureCb)
        viewMenu.addItem('-', None)
        jsresolver = "genro.rpc.remoteResolver('getQuickView',null,{cacheTime:'5'})"
        viewMenu.addItem('savedview', jsresolver, _T='JS', caption='!!Custom view',
                         action='FIRE list.view_id = $1.pkey;')
        viewMenu.setItem('editview', None, caption='!!Edit view', action="""
                                                                    SET list.showToolbox = true;
                                                                    SET list.toolboxSelected = 'view';
                                                                    """)
        viewMenu.setItem('saveview', None, caption='!!Save view', action="FIRE list.save_userobject='view';")
        pane.data('list.view.menu', viewMenu)
        pane.data('list.view.pyviews', structures, baseview='_base')

    def listCustomCbBag(self, prefix=None, basename=None, cb=None):
        cblist = sorted(
                [func_name for func_name in dir(self) if func_name.startswith(prefix) and func_name != prefix]) or []
        if basename:
            cblist = [basename] + cblist
        menuBag = Bag()
        for funcname in cblist:
            name = funcname[len(prefix):]
            handler = getattr(self, funcname)
            label = name or '_base'
            if cb:
                cb(label, handler)
            menuBag.setItem(label, None, caption=handler.__doc__ or name.title() or 'Base')
        return menuBag

    def listController(self, pane):
        pane.data('list.excludeLogicalDeleted', True)
        pane.data('aux.showDeleted', False)
        self.listViewStructures(pane)
        pane.dataController(
                """genro.querybuilder = new gnr.GnrQueryBuilder("query_root", "%s", "list.query.where");""" % self.maintable
                , _init=True)
        pane.dataController(
                """genro.queryanalyzer = new gnr.GnrQueryAnalyzer("translator_root","list.query.where","list.runQueryDo")"""
                , _onStart=True)
        pane.dataController("""genro.querybuilder.createMenues();
                                  dijit.byId('qb_fields_menu').bindDomNode(genro.domById('fastQueryColumn'));
                                  dijit.byId('qb_not_menu').bindDomNode(genro.domById('fastQueryNot'));
                                  genro.querybuilder.buildQueryPane();""", _onStart=True)
        pane.data('usr.writePermission', self.userCanWrite())
        pane.data('usr.deletePermission', self.userCanDelete())
        pane.data('usr.unlockPermission', self.userCanDelete() or self.userCanWrite())
        pane.dataFormula('status.locked', 'true', _onStart=True)
        condition = self.conditionBase()
        condPars = {}
        if condition:
            condPars = condition[1] or {}
            condition = condition[0]
        pane.data('list.plural', self.pluralRecordName())
        pane.data('list.rowcount', 0)

        if self.tableRecordCount():
            pane.dataRpc('list.rowtotal', 'app.getRecordCount', _onStart=300,
                         table=self.maintable, where=condition, **condPars)

        pane.dataController("""var listtitle=rowtotal?plural+' : '+rowcount+'/'+rowtotal:plural+' : '+rowcount
                               SET list.title_bar=listtitle;
                               var titlebar=(selectedPage == 0)?listtitle:formtitle;
                               genro.publish('public_caption',titlebar)""",
                         selectedPage='^selectedPage', plural='^list.plural', rowcount='^list.rowcount',
                         rowtotal='^list.rowtotal',
                         formtitle='^form.title', _init=True)

        #pane.data('list',dict(plural=self.pluralRecordName(), rowcount=0,
        #                      rowtotal=self.tblobj.query(where=condition,**condPars).count())) # mettere come RPC per aggiornare non solo al caricamento

        pane.dataFormula('list.canWrite', '(!locked ) && writePermission', locked='^status.locked',
                         writePermission='=usr.writePermission', _init=True)
        pane.dataFormula('list.canDelete', '(!locked) && deletePermission', locked='^status.locked',
                         deletePermission='=usr.deletePermission', _init=True)
        pane.dataController("SET list.selectedIndex=-1; SET selectedPage = 1", fired='^list.newRecord')
        pane.dataController(""" var pkey;
                                console.log(idx);
                                    if (idx < -1){
                                        pkey = null;
                                        PUT list.selectedIndex = null;
                                        SET selectedPage=0; 
                                        SET list.query.pkeys=null;
                                        return;
                                    }
                                    else if (idx == -1){
                                                        pkey = '*newrecord*';
                                                        PUT list.selectedIndex = null;}
                                    else {
                                          pkey = genro.wdgById("maingrid").rowIdByIndex(idx);
                                         }
                                    if(pkey){
                                        SET list.selectedId = pkey;
                                        FIRE form.doLoad = true;
                                    } 
                                    """,
                            idx='^list.selectedIndex')
        pane.dataController("SET status.locked=true;", fired='^status.lock')
        pane.dataController("SET status.locked=false;", fired='^status.unlock', _if='unlockPermission',
                            unlockPermission='=usr.unlockPermission',
                            forbiddenMsg='==  unlockForbiddenMsg || dfltForbiddenMsg',
                            unlockForbiddenMsg='=usr.unlockForbiddenMsg',
                            dfltForbiddenMsg="!!You cannot unlock this table",
                            _else='FIRE gnr.alert = forbiddenMsg')

        pane.dataController("""genro.dlg.ask(askTitle, message,
                                                {export:exportButton, print:printButton, pdf:pdfButton, actions:actionsButton, cancel:cancelButton},
                                                'list.onSelectionCommands');""",
                            fired='^list.onSelectionMenu', askTitle='!!Commands',
                            message="!!Export or Print the selection",
                            exportButton="!!Export", printButton="!!Print", pdfButton='!!Pdf', actionsButton='!!Actions'
                            , cancelButton='!!Cancel')
        pane.dataController("""
            //var pkeys = genro.wdgById("maingrid").getSelectedPkeys();
            var selectedRowidx = genro.wdgById("maingrid").getSelectedRowidx();
            if(command=='print'){
                var url = genro.rpc.rpcUrl("app.onSelectionDo", {table:table, selectionName:selectionName, command:'print',
                                                             callmethod:null, selectedRowidx:selectedRowidx})
                genro.dev.printUrl(url);
            }
            else if((command=='export')||(command='pdf')){
                //var url = genro.rpc.rpcUrl("app.onSelectionDo", {table:table, selectionName:selectionName, command:command,
                //                                            callmethod:null, selectedRowidx:selectedRowidx})
                
                genro.download('', {method:"app.onSelectionDo",table:table, selectionName:selectionName, command:command,
                                                             callmethod:null, selectedRowidx:selectedRowidx});
            }
            else if(command=='actions'){
                genro.dlg.listChoice(act_title, act_msg, {confirm:btn_confirm,cancel:btn_cancel},
                                     act_resultPath, act_valuePath, act_storePath);
            }
            """, #### MODIFICA MIKI 30 gennaio 2009
                            command='^list.onSelectionCommands',
                            table=self.maintable,
                            selectionName='=list.selectionName',
                            act_title='!!Actions',
                            act_msg='!!Choose the action to execute: ',
                            btn_confirm='!!Confirm',
                            btn_cancel='!!Cancel',
                            act_resultPath='list.act_result',
                            act_valuePath='list.act_value',
                            act_storePath='list.act_store'
                            )
        act_bag = Bag()
        for action in [m[7:] for m in dir(self) if m.startswith('action_')]:
            act_bag[action] = '!!%s' % action.capitalize().replace('_', ' ')
        pane.data('list.act_store', act_bag, id='#k', caption='#v')
        pane.dataController("""var selectedRowidx = genro.wdgById("maingrid").getSelectedRowidx();
                                   genro.serverCall('app.onSelectionDo', {table:table, selectionName:selectionName, command:'action',
                                                     callmethod:action, selectedRowidx:selectedRowidx}, 'function(result){genro.dlg.alert(result)}')"""
                            ,
                            confirm='^list.act_result', action='=list.act_value', _if='confirm=="confirm"',
                            table=self.maintable, selectionName='=list.selectionName')

    def listToolbar(self, pane):
        toolbarKw = dict()
        tagSlot = ''
        tagFilter = ''
        if self.hasTags():
            tagSlot = '15,|,tagsbtn,|,'
            toolbarKw['tagsbtn_mode'] = 'list'
        if self.enableFilter():
            tagFilter = 'filtermenu,'
        pane.slotToolbar('left_top_opener,|,5,queryfb,iv_runbtn,%sviewmenu,%s*,|,form_add,form_locker,5' %(tagSlot,tagFilter),
                        iv_runbtn_action='FIRE list.runQueryButton;',form_add_parentForm='formPane',
                        form_locker_parentForm='formPane',**toolbarKw)

    @struct_method
    def th_mainlist_left_top_opener(self,pane,**kwargs):
        pane.button('!!Show Fields',iconClass='db_treebtn', showLabel=False,action="SET list.showToolbox = ! (GET list.showToolbox);")
        pane.button('!!Extended Query',iconClass='db_querybtn',showLabel=False, action="SET list.showExtendedQuery =! (GET list.showExtendedQuery);")        
   
    @struct_method
    def th_mainlist_viewmenu(self,pane,**kwargs):
        ddb = pane.dropdownbutton('!!Select view', showLabel=False,
                                     iconClass='vieselectorIcn', _class='dropDownNoArrow')
        ddb.menu(_class='smallmenu', storepath='list.view.menu',
                 action="""
                            SET list.view.pyviews?baseview = $1.fullpath;
                            //to correct the path name
                            FIRE list.view.new; 
                            //end to correct
                            if(GET list.selectionName){
                                FIRE list.runQuery;
                            }
                           """)
   
    @struct_method
    def th_mainlist_queryfb(self, pane,**kwargs):
        queryfb = pane.formbuilder(cols=5, datapath='.query.where', _class='query_form',
                                   border_spacing='0', onEnter='genro.fireAfter("list.runQuery",true,10);',
                                   float='left')
        queryfb.div('^.c_0?column_caption', min_width='12em', _class='smallFakeTextBox floatingPopup',
                    nodeId='fastQueryColumn',
                     dropTarget=True,
                    lbl='!!Search',**{'onDrop_gnrdbfld_%s' %self.maintable.replace('.','_'):"genro.querybuilder.onChangedQueryColumn(this,data);"})
        optd = queryfb.div(_class='smallFakeTextBox', lbl='!!Op.', lbl_width='4em')

        optd.div('^.c_0?not_caption', selected_caption='.c_0?not_caption', selected_fullpath='.c_0?not',
                 display='inline-block', width='1.5em', _class='floatingPopup', nodeId='fastQueryNot',
                 border_right='1px solid silver')
        optd.div('^.c_0?op_caption', min_width='7em', nodeId='fastQueryOp', readonly=True,
                 selected_fullpath='.c_0?op', selected_caption='.c_0?op_caption',
                 connectedMenu='==genro.querybuilder.getOpMenuId(_dtype);',
                 action="genro.querybuilder.onChangedQueryOp($2,$1);",
                 _dtype='^.c_0?column_dtype',
                 _class='floatingPopup', display='inline-block', padding_left='2px')
        value_textbox = queryfb.textbox(lbl='!!Value', value='^.c_0', width='12em', lbl_width='5em',
                                        _autoselect=True,
                                        row_class='^.c_0?css_class', position='relative',
                                        disabled='==(_op in genro.querybuilder.helper_op_dict)', _op='^.c_0?op',
                                        validate_onAccept='genro.queryanalyzer.checkQueryLineValue(this,value);',
                                        _class='st_conditionValue')

        value_textbox.div('^.c_0', hidden='==!(_op in genro.querybuilder.helper_op_dict)',
                          connect_onclick="if(GET .c_0?op in genro.querybuilder.helper_op_dict){FIRE list.helper.queryrow='c_0';}"
                          ,
                          _op='^.c_0?op', _class='helperField')
        
        queryfb.dataFormula('list.currentQueryCountAsString', 'msg.replace("_rec_",cnt)',
                            cnt='^list.currentQueryCount', _if='cnt', _else='',
                            msg='!!Current query will return _rec_ items')
        queryfb.dataController("""if(fired=='Shift'){
                                     FIRE list.showQueryCountDlg;
                                     }else{
                                         FIRE list.runQuery;
                                     }""", fired='^list.runQueryButton')
        queryfb.dataController("""SET list.currentQueryCountAsString = waitmsg;
                                     genro.fireAfter('list.updateCurrentQueryCount');
                                     genro.dlg.alert('^list.currentQueryCountAsString',dlgtitle);
                                  """, _fired="^list.showQueryCountDlg", waitmsg='!!Working.....',
                               dlgtitle='!!Current query record count')

    def pageListController(self, pane):
        """docstring for pageListController"""
        pane.dataController('SET list.noSelection=true;SET list.rowIndex=null;', fired='^list.runQuery', _init=True)
        pane.dataController("""genro.dom.disable("query_buttons");
                               SET list.gridpage = 1;
                               genro.querybuilder.cleanQueryPane();
                               SET list.queryRunning = true;
                               var parslist = genro.queryanalyzer.translateQueryPars();
                               if (parslist.length>0){
                                  genro.queryanalyzer.buildParsDialog(parslist);
                               }else{
                                  FIRE list.runQueryDo = true;
                               }
                               
                               """,
                            running='=list.queryRunning', _if='!running', fired='^list.runQuery')
        pane.dataController('SET list.query.selectedId = query_id; genro.fireAfter("list.runQueryButton",true,300)',
                            query_id="^list.query_id")
        pane.dataController("""SET list.view.selectedId = view_id; 
                                if(selectionName){
                                    genro.fireAfter("list.runQueryButton",true,300);
                                }
                                """,
                            view_id="^list.view_id", selectionName='=list.selectionName')

        pane.dataController("""if((!initialPkey) && (window.location.hash.indexOf('#pk_')==0)){
                                    initialPkey=window.location.hash.slice(4);
                                    if(initialPkey == '*newrecord*') {
                                        initialPkey = null;
                                        window.location.hash = '';
                                    }
                                    SET initialPkey=initialPkey;
                                }
                                if(initialPkey){
                                    SET selectedPage=1;
                                    SET list.query.pkeys=initialPkey;
                                    FIRE list.runQuery = true;
                                }
                                   """,
                            _onStart=.5, initialPkey='=initialPkey') # pkg/page#pk_*newrecord* disabled because it doesn't work

        pane.dataController("""var pkeys= genro.getData('list.'+dataset_name);
                                   if(pkeys){
                                       SET list.query.pkeys=pkeys;
                                       FIRE list.runQuery = true;
                                   }""",
                            dataset_name='^list.querySet')

        pane.dataController('genro.wdgById("maingrid").updateRowCount(rowcount)', rowcount='^list.rowcount')

        pane.dataController("""
                                   var nodeStart=genro.getDataNode('list.grid.store');
                                   var grid=genro.wdgById("maingrid");
                                   //grid.clearBagCache();
                                   var rowcount=nodeStart.attr.totalrows;
                                   
                                   SET list.rowcount = rowcount;
                                   SET list.rowtotal = nodeStart.attr.totalRowCount;
                                   SET list.selectionName = nodeStart.attr.selectionName;
                                   //grid.updateRowCount(0);
                                   //grid.updateRowCount(rowcount);
                                   //grid.selection.unselectAll();                            
                                   genro.dom.enable("query_buttons");
                                   SET list.queryRunning = false;
                                   SET list.gridpage = 0;
                                   PUT list.selectedIndex=null;
                                   if(initialPkey){
                                       SET list.selectedIndex=0;
                                       SET initialPkey=null;
                                   }
                                """, fired='^list.queryEnd', initialPkey='=initialPkey')

    def listBottomPane(self, bc, **kwargs):
        """
        CALLBACK of standardTable
        """
        bottomPane_list = sorted([func_name for func_name in dir(self) if func_name.startswith('bottomPane_')])
        if not bottomPane_list:
            return
        pane = bc.contentPane(_class='listbottompane', datapath='list.bottom', overflow='hidden', **kwargs)
        fb = pane.formbuilder(cols=15, border_spacing='2px')
        for func_name in bottomPane_list:
            getattr(self, func_name)(fb.div(datapath='.%s' % func_name[11:]))

    def onQueryCalling(self):
        return None

    def gridPane(self, pane):
        lstkwargs = dict()
        stats_main = getattr(self, 'stats_main', None)
        if self.hierarchicalViewConf() or self.hierarchicalEdit() or stats_main:
            tc = pane.tabContainer(selected='^list.selectedTab')
            gridpane = tc.contentPane(title='!!Standard view')
            if stats_main:
                stats_main(tc, datapath='stats', title='!!Statistical view')
            if self.hierarchicalViewConf():
                self.hv_main_view(tc.borderContainer(title='!!Hierarchical view', datapath='list.hv.view'))
            if self.hierarchicalEdit():
                self.hv_main_form(tc.borderContainer(title='!!Hierarchical edit', datapath='list.hv.edit'))

        else:
            gridpane = pane
        pane.data('.sorted', self.orderBase())
        condition = self.conditionBase()
        condPars = {}
        if condition:
            condPars = condition[1] or {}
            condition = condition[0]
        pane.dataController("""
        var columns = gnr.columnsFromStruct(struct);
        if(hiddencolumns){
            var hiddencolumns = hiddencolumns.split(',');
            columns = columns+','+hiddencolumns;
        }
        
        SET .columns = columns;
        """, hiddencolumns=self.hiddencolumnsBase(),
                            struct='^list.view.structure', _init=True)

        pane.data('list.tableRecordCount', self.tableRecordCount())

        customOnDrops = dict(
                [('onDrop_%s' % k[10:], getattr(self, k)()) for k in dir(self) if k.startswith('lstOnDrop_')])
        lstkwargs.update(customOnDrops)
        dbfieldcode = 'gnrdbfld_%s' % self.maintable.replace('.', '_')
        lstkwargs[
        'onDrop_%s' % dbfieldcode] = "this.widget.addColumn(data,dropInfo.column);if(this.widget.rowCount>0){genro.fireAfter('list.runQueryDo',true);}"

        iv = gridpane.includedView(parentFrame='mainlist',nodeId='maingrid', 
                                 structpath="list.view.structure", autoWidth=False,
                                 datapath='.wdg',
                                 selectedIndex='list.rowIndex', rowsPerPage=self.rowsPerPage(), sortedBy='^list.grid.sorted',
                                 _newGrid=True,
                                 connect_onSelectionChanged='SET list.noSelection = (genro.wdgById("maingrid").selection.getSelectedCount()==0)',
                                 linkedForm='formPane', openFormEvent='onRowDblClick', dropTypes=None,
                                 dropTarget=True,
                                 selfDragColumns='trashable',
                                 dropTarget_column=dbfieldcode,
                                 dropTarget_grid='explorer_*',
                                 onDrop_gnrdbfld="""this.widget.addColumn(data,dropInfo.column);if(this.widget.rowCount>0){genro.fireAfter('list.runQueryDo',true);}"""
                                 ,
                                 onDrop_gridrow='console.log("dropped gridrow");console.log(data);',
                                 draggable=True, draggable_row=True,
                                 dragClass='draggedItem',
                                 onDrop=""" for (var k in data){
                                                 this.setRelativeData('list.external_drag.'+k,new gnr.GnrBag(data[k]));
                                              }""",
                                 connect_onRowContextMenu="FIRE list.onSelectionMenu = true;",
                                 **lstkwargs)
                             
        store = iv.selectionStore(table=self.maintable, columns='=.columns',
                           chunkSize=self.rowsPerPage()*4,
                           where='=list.query.where', sortedBy='=list.grid.sorted',
                           pkeys='=list.query.pkeys', _fired='^list.runQueryDo',
                           selectionName='*', recordResolver=False, condition=condition,
                           sqlContextName='standard_list', totalRowCount='=list.tableRecordCount',
                           row_start='0', 
                           excludeLogicalDeleted='^list.excludeLogicalDeleted',
                           applymethod='onLoadingSelection',
                           timeout=180000, selectmethod='=list.selectmethod',
                           selectmethod_prefix='customQuery',
                           _onCalling=self.onQueryCalling(),
                           **condPars)
        store.addCallback('FIRE list.queryEnd=true; SET list.selectmethod=null; return result;')

        pane.dataController("SET list.selectedIndex = idx; SET selectedPage = 1;",
                            idx="^gnr.forms.formPane.openFormIdx")

        pane.dataRpc('list.currentQueryCount', 'app.getRecordCount', condition=condition,
                     fired='^list.updateCurrentQueryCount',
                     table=self.maintable, where='=list.query.where',
                     excludeLogicalDeleted='=list.excludeLogicalDeleted',
                     **condPars)
        pane.dataController("""genro.setData("list.query.where",baseQuery.deepCopy(),{objtype:"query", tbl:maintable});
                               genro.querybuilder.buildQueryPane(); 
                               SET list.view.selectedId = null;
                               if(!fired&&runOnStart){
                                    FIRE list.runQuery
                               }
                            """,
                            _onStart=True, baseQuery='=list.baseQuery', maintable=self.maintable,
                            fired='^list.query.new',
                            runOnStart=self.queryBase().get('runOnStart', False))
        pane.data('list.baseQuery', self.queryFromQueryBase())


        #btnpane.button('Add View', iconClass='tb_button db_add', fire='list.view.new',showLabel=False)

    def queryFromQueryBase(self):
        result = Bag()
        querybase = self.queryBase()
        op_not = querybase.get('op_not', 'yes')
        column = querybase.get('column')
        column_dtype = None
        if column:
            column_dtype = self.tblobj.column(column).getAttr('dtype')
        not_caption = '&nbsp;' if op_not == 'yes' else '!!not'
        result.setItem('c_0', querybase.get('val'),
                       {'op': querybase.get('op'), 'column': column,
                        'op_caption': '!!%s' % self.db.whereTranslator.opCaption(querybase.get('op')),
                        'not': op_not, 'not_caption': not_caption,
                        'column_dtype': column_dtype,
                        'column_caption': self.app._relPathToCaption(self.maintable, column)})
        return result

