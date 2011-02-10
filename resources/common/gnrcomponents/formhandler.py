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
from gnr.core.gnrdict import dictExtract


class FormHandler(BaseComponent):
    css_requires='public'
    py_requires='foundation/macrowidgets:SlotBar'

    @struct_method
    def fh_slotbar_navigation(self,pane,**kwargs):
        pane = pane.div(lbl='!!Navigation',_class='slotbar_group')
        pane.slotbar_first()
        pane.slotbar_prev()
        pane.slotbar_next()
        pane.slotbar_last()
    
    @struct_method               
    def fh_slotbar_semaphore(self,pane,**kwargs):
        pane.div(_class='fh_semaphore')
    
    @struct_method          
    def fh_slotbar_formcommands(self,pane,**kwargs):
        pane = pane.div(lbl='!!Form Commands',_class='slotbar_group')
        pane.slotbar_save()
        pane.slotbar_revert()
        pane.slotbar_delete()

    
    @struct_method          
    def fh_slotbar_save(self,pane,**kwargs):
        pane.formButton('!!Save',topic='save',iconClass="tb_button db_save", parentForm=True)

    @struct_method          
    def fh_slotbar_revert(self,pane,**kwargs):
        pane.formButton('!!Revert',topic='load',iconClass="tb_button db_revert", parentForm=True)
    
    @struct_method          
    def fh_slotbar_delete(self,pane,**kwargs):
        pane.formButton('!!Delete',topic='delete',iconClass="tb_button db_del",parentForm=True)

    @struct_method          
    def fh_slotbar_first(self,pane,**kwargs):
        pane.formButton('!!First',iconClass="tb_button icnNavFirst",
                    topic='navigationEvent',command='first',
                    formsubscribe_navigationStatus="this.widget.setAttribute('disabled',$1.first || false);")
    
    @struct_method          
    def fh_slotbar_prev(self,pane,**kwargs):
        pane.formButton('!!Prev',iconClass="tb_button icnNavPrev",
                    topic='navigationEvent',command='prev',
                    formsubscribe_navigationStatus="this.widget.setAttribute('disabled',$1.first || false);")
    
    @struct_method          
    def fh_slotbar_next(self,pane,**kwargs):
        pane.formButton('!!Next',iconClass="tb_button icnNavNext",
                    topic='navigationEvent',command='next',
                    formsubscribe_navigationStatus="this.widget.setAttribute('disabled',$1.last || false);")
    
    @struct_method          
    def fh_slotbar_last(self,pane,**kwargs):
        pane.formButton('!!Last',iconClass="tb_button icnNavLast",
                    topic='navigationEvent',command='last',
                    formsubscribe_navigationStatus="this.widget.setAttribute('disabled',$1.last || false);")

    @struct_method           
    def fh_formButton(self,pane,label=None,iconClass=None,topic=None,command=True,**kwargs):
        pane.button(label, lbl=label,iconClass=iconClass,topic=topic,
                    action='this.form.publish(topic,command);',command=command,
                    showLabel=False,**kwargs)
    
    @struct_method 
    def fh_slotbar_locker(self,pane,**kwargs):
        pane.button('!!Locker',width='20px',iconClass='icnBaseUnlocked',showLabel=False,
                    action='this.form.publish("setLocked","toggle");',
                    formsubscribe_onLockChange="""var locked= $1.locked;
                                                  this.widget.setIconClass(locked?'icnBaseLocked':'icnBaseUnlocked');""")
        
    @struct_method
    def recordClusterStore(self,pane,table=None,storeType=None,**kwargs):
        form_table = table or self.maintable
        pane.attributes['form_table'] = form_table
        pane.formStore('recordCluster',storeType=storeType,loadMethod='loader_recordCluster',
                        saveMethod='saver_recordCluster',deleteMethod='deleter_recordCluster',
                        **kwargs)
               