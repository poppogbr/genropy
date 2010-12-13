# -*- coding: UTF-8 -*-

# grid_configurator.py
# Created by Francesco Porcari on 2010-10-02.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag

class ChunkEditor(BaseComponent):
    py_requires='foundation/dialogs,foundation/macrowidgets:RichTextEditor'
    
    def htmlChunk(self,pane,nodeId=None,data=None,dflt=None,table=None,**kwargs):
        pane.div(innerHTML="==dataTemplate(tpl,data)",
                tpl="^gnr.htmlchunk.%s.content" %nodeId,
                data=data,
                connect_ondblclick="""console.log('ondblclick')
                                      SET gnr.htmlchunk.editor.path ='gnr.htmlchunk.%s';
                                      var table = GET gnr.htmlchunk.%s.table;
                                      FIRE #chunkeditor.open;
                                      if(table){
                                        genro.dev.relationExplorer(table,'Table');
                                      }
                                    """ %(nodeId,nodeId),
                nodeId=nodeId,**kwargs)
                
        loadedchunk = self.rpc_loadChunk(code=nodeId,dflt=dflt)
        controller = pane.dataController(datapath='gnr.htmlchunk.%s' %nodeId)
        controller.data('.content',loadedchunk)
        controller.dataFormula('.table','table',table='%s?table' %data)
        controller.dataRpc('dummy','saveChunk',code=nodeId,data='=.content',_fired='^#chunkeditor.save',
                            _onResult='FIRE #chunkeditor.close')
        
        
    
    
    def onMain_chunkeditor(self):
        if not self.isDeveloper():
            return
        page = self.pageSource()
        dlgBc = self.simpleDialog(page,title='!!Chunk editor',datapath='gnr.htmlchunk.editor',
                                dlgId='chunkeditor',height='400px',width='700px')
        bc = dlgBc.borderContainer(region='center')
        #self.chunkeditor_tree(bc.contentPane(region='left',margin='5px',splitter=True,width='250px'))
        self.chunkeditor_editor(bc.contentPane(region='center',margin='5px',datapath='^gnr.htmlchunk.editor.path'))
        
       #dlgBc.dataRpc('dummy','loadChunk',pkey='^.opener.chunk_id',_onResult="""SET .table=result.attr.tbl;
       #                                                                        SET .content = """)
        

    def chunkeditor_editor(self,pane):
        self.RichTextEditor(pane, value='^.content',height='100%',
                            toolbar=self.rte_toolbar_standard(),)

    def chunkeditor_tree(self,pane):
        pane.dataRemote('.tree.fields','relationExplorer',
                        table='^.table',
                        dosort=False,caption='Fields')
        pane.tree(storepath='.tree',persist=False,
                     labelAttribute='caption',
                     _class='fieldsTree',
                     hideValues=True,
                     nodeId='ffff',
                     margin='6px',
                     font_size='.9em',
                     draggable=True,
                     onDrag="""
                                if(!(treeItem.attr.dtype && treeItem.attr.dtype!='RM' && treeItem.attr.dtype!='RO')){
                                    return false;
                                }
                                dragValues['text/html']='$'+treeItem.attr.fieldpath;
                                dragValues['text/plain'] =treeItem.attr.fieldpath;
                              """,                     
                     getLabelClass="""if (!node.attr.fieldpath && node.attr.table){return "tableTreeNode"}
                                        else if(node.attr.relation_path){return "aliasColumnTreeNode"}
                                        else if(node.attr.sql_formula){return "formulaColumnTreeNode"}""",
                     getIconClass="""if(node.attr.dtype){return "icnDtype_"+node.attr.dtype}
                                     else {return opened?'dijitFolderOpened':'dijitFolderClosed'}""")

    def rpc_deleteChunk(self,pkey=None):
        self.package.deleteUserObject(pkey)
        self.db.commit()

    def rpc_saveChunk(self,code=None,data=None):
        objtype = 'htmlchunk_%s' %self.pagename
        self.package.saveUserObject(Bag(dict(content=data)), code=code, 
                                    objtype=objtype)
        self.db.commit()
        
    def rpc_loadChunk(self,code=None,dflt=None):
        objtype = 'htmlchunk_%s' %self.pagename
        data, metadata = self.package.loadUserObject(code=code,objtype=objtype)
        data = data or Bag()
        return data['content'] or dflt
    