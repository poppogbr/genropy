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



"""
Component for menu handling:
"""
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag,BagResolver
import os

class Menu(BaseComponent):
    css_requires = 'menu'
    
   #def onMain_menuInit(self):
   #    self.pageSource().data('gnr.appmenu',MenuResolver(path=None))
   #
    def menu_menuPane(self,parentBC,**kwargs):
        b=Bag()
        b['root']=MenuResolver(path=None)
        parentBC.data('gnr.appmenu',b)
        leftPane = parentBC.contentPane(width='20%',_class='menupane',**kwargs)
        leftPane.tree(id="_gnr_main_menu_tree",storepath='gnr.appmenu.root',selected_file='gnr.filepath',
                       labelAttribute='label',
                       hideValues=True,
                       _class='menutree',
                       persist='site',
                       inspect='shift',
                       identifier='#p',
                       getIconClass='return node.attr.iconClass || "treeNoIcon"',
                       getLabelClass='return node.attr.labelClass',
                       openOnClick=True,
                       #connect_onClick='genro.gotoURL($1.getAttr("file"),true)',
                       #getLabel="""return "<a href='"+node.attr.file+"'>"+node.attr.label+"</a>::HTML";""",
                       getLabel="""if(node.attr.file){ return 'innerHTML:<a href="'+node.attr.file+'"><div style="width:100%;height:100%;">'+node.attr.label+'</div></a>'}else  {return node.attr.label};""",
                       nodeId='_menutree_')
        leftPane.dataController("genro.wdgById('_gnrRoot').showHideRegion('left', false);",fired='^gnr.onStart',
                                appmenu="=gnr.appmenu",_if="appmenu.len()==0")
        
        
    def getUserMenu(self, fullMenubag):
        def userMenu(userTags,menubag,level,basepath):
            result = Bag()
            #if not userTags:
                #return result
            for node in menubag.nodes:
                allowed=True
                nodetags=node.getAttr('tags')
                if nodetags:
                    allowed=self.application.checkResourcePermission(nodetags, userTags)
                if allowed and node.getAttr('file'):
                    allowed = self.checkPermission(node.getAttr('file'))
                if allowed:
                    value=node.getStaticValue()
                    attributes={}
                    attributes.update(node.getAttr())
                    currbasepath=basepath
                    if 'basepath' in attributes:
                        newbasepath=node.getAttr('basepath')
                        if newbasepath.startswith('/'):
                            currbasepath=[self.site.home_uri+newbasepath[1:]]
                        else:
                            currbasepath=basepath+[newbasepath]
                    if isinstance(value,Bag):
                        value = userMenu(userTags,value,level+1,currbasepath)
                        labelClass = 'menu_level_%i' %level 
                    else:
                        value=None
                        labelClass = 'menu_page'
                    customLabelClass = attributes['customLabelClass'] or ''
                    attributes['labelClass'] = 'menu_shape %s %s' %(labelClass, customLabelClass)
                    filepath=attributes.get('file')
                    if filepath: 
                        if not filepath.startswith('/'):
                            attributes['file'] = os.path.join(*(currbasepath+[filepath]))
                        else:
                            attributes['file'] = self.site.home_uri + filepath.lstrip('/')
                    result.setItem(node.label,value,attributes)
            return result
        result=userMenu(self.userTags,fullMenubag,0,[])
        while len(result)==1:
            result=result['#0']
        return result
        
class MenuResolver(BagResolver):
    classKwargs={'cacheTime':300,
                 'readOnly':False,
                 'path':None}
    classArgs=['path']
    def load(self):
        sitemenu = self._page.application.siteMenu
        userTags=self._page.userTags
        result = Bag()
        level = 0
        if self.path:
            level = len(self.path.split('.'))
        for node in sitemenu[self.path].nodes:
            allowed=True
            nodetags=node.getAttr('tags')
            filepath=node.getAttr('file')
            if nodetags:
                allowed=self._page.application.checkResourcePermission(nodetags, userTags)
            if allowed and filepath:
                allowed = self._page.checkPermission(filepath)
            if allowed:
                value=node.getStaticValue()
                attributes={}
                attributes.update(node.getAttr())
                if isinstance(value,Bag):
                    newpath = node.label
                    if self.path:
                        newpath = '%s.%s' %(self.path,node.label)
                    else:
                        newpath = node.label
                    value = MenuResolver(path=newpath)
                    labelClass = 'menu_level_%i' %level 
                else:
                    value=None
                    labelClass = 'menu_page'             
                customLabelClass = attributes.get('customLabelClass','')
                attributes['labelClass'] = 'menu_shape %s %s' %(labelClass, customLabelClass)
                result.setItem(node.label,value,attributes)
        return result
            
   