# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-02-25.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method

class PluggedPageManager(BaseComponent):
    
    @struct_method
    def ppm_pluginTabs(self,parent,plugins=None,startPos=None,datapathTemplate=None,remoteTemplate=None,disabled=None):
        # print 'plugins'
        # print plugins
        parent.dataController("""
            //console.log('plugins');
            //console.log(+plugins);
            var sourceNode = this.getParentNode();
            plugins = plugins? plugins.toLowerCase():'';
            var tablist = plugins.split(',');
            var content = sourceNode.getValue('static');
            var k = startPos;
            var currNode,p;
            dojo.forEach(tablist,function(plugin){
                if(!content.getItem(plugin)){
                var dpath = datapathTemplate?datapathTemplate.replace('$',plugin):null;
                p = sourceNode._('BorderContainer',plugin,{'title':plugin.toUpperCase(),
                                                        nodeId:plugin+'_plugin_tab',
                                                    _plugin:true,pageName:'plugin_'+plugin,
                                                    datapath:dpath},
                            {'_position':k});
                p._('BorderContainer',{region:'center',_lazyBuild:'ppm_pluginTab',
                                    remote_handlerName:remoteTemplate.replace('$',plugin),
                                    remote_disabled:disabled});
                }else{
                    currNode = content.getNode('#'+k);
                    while(currNode &&(currNode.label!=plugin)&&(currNode.attr._plugin==true)){
                        content.popNode('#'+k);
                        currNode = content.getNode('#'+k);
                    }
                }
                k++;
            });
            while(k<content.len()){
            if(content.getNode('#'+k).attr._plugin){
                content.popNode('#'+k);
            }else{
                k++;
            }
            sourceNode.widget.layout();
    }   
    """,plugins=plugins,datapathTemplate=datapathTemplate,startPos=startPos or len(parent),
        remoteTemplate=remoteTemplate,disabled=disabled.replace('^',''))
    
    def remote_ppm_pluginTab(self,pane,handlerName=None,**kwargs):
        handler = getattr(self, handlerName)
        if 'disabled' in kwargs:
            kwargs['disabled'] = '^%s' %kwargs['disabled']
        handler(pane,**kwargs)

        