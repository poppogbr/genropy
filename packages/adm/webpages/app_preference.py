#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Preference
#
#  Created by Francesco Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

class GnrCustomWebPage(object):
    maintable ='adm.preference'
    py_requires="""public:Public"""   
    
    def windowTitle(self):
         return '!!Preference panel'
         
    def mainLeftContent(self,parentBC,**kwargs):
        return
        
    def rootWidget(self, root, **kwargs):
        return root.borderContainer(_class='pbl_dialog_center',**kwargs)
        
    def onIniting(self, url_parts, request_kwargs):
        for pkgname in self.db.packages.keys():
            try:
                cl=self.site.loadResource(pkgname,'preference:AppPref')
                self.mixin(cl) 
            except:
                pass
                
    def main(self, rootBC, **kwargs):
        """APPLICATION PREFERENCE BUILDER"""
        self.controllers(rootBC)
        self.bottom(rootBC.contentPane(region='bottom',_class='dialog_bottom'))    
        tc = rootBC.tabContainer(region='center',datapath='preference',formId='preference')
        for pkg in self.db.packages.values():
            panecb = getattr(self,'prefpane_%s' %pkg.name,None)
            if panecb:
                panecb(tc,title=pkg.name_full,datapath='.%s' %pkg.name,nodeId=pkg.name)

    def bottom(self,bottom):
        bottom.button('!!Apply settings',baseClass='bottom_btn',float='right',margin='1px',
                        action='genro.formById("preference").save(true)')
        bottom.button('!!Cancel',baseClass='bottom_btn',float='right',margin='1px',
                        fire='frame.close')    
                        
    def controllers(self,pane):
        pane.dataController("""parent.genro.fireEvent("#mainpreference.close");""",_fired="^frame.close")
        pane.dataController("genro.formById('preference').load()",_onStart=True)
        pane.dataRpc('dummy','savePreference',preference='=preference',nodeId='preference_saver',
                    _onResult='genro.formById("preference").saved();FIRE frame.close;')
        pane.dataRpc('preference','loadPreference',nodeId='preference_loader',
                     _onResult='genro.formById("preference").loaded();')
        
    def rpc_loadPreference(self):
        return self.loadAppPreference()
    
    def rpc_savePreference(self,preference):
        self.saveAppPreference(preference)
        return
 