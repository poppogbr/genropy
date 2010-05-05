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
Component for thermo:
"""
from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrstring import toText
from gnr.core.gnrdate import dayIterator
from babel import dates

def rect(**kwargs):
    result = dict(position='absolute')
    for k,v in kwargs.items():
        if v is not None:
            result[k] = '%ipx' %v
    return result

class Timetable(BaseComponent):
    py_requires='foundation/tools:RemoteBuilder,foundation/tools:CSSHandler'
    css_requires='public'
    def tt_colorPaletteMenu(self,parent):
        parent.div().menu(modifiers='*',id='tt_colorPaletteMenu',_class='colorPaletteMenu',
                            connect_onOpen="""
                                            var path= this.widget.originalContextTarget.sourceNode.absDatapath();
                                             SET _temp.ttcolor=path;""",
                        ).menuItem(datapath='^_temp.ttcolor').colorPalette(value='^.color',connect_ondblclick='dijit.byId("tt_colorPaletteMenu").onCancel();')
        
        
    def timetable_dh(self,parent,nodeId=None,datapath=None,tstart=None,
                    tstop=None,period=None,wkdlist=None,series=None,fired=None):
        assert nodeId,'nodeId is mandatory'
        assert datapath,'datapath is mandatory'
        assert hasattr(self,'tt_%s_dataProvider'%nodeId), 'you must define your own loop'
        parent.style(self.tt_localcss())
        
        bc = parent.borderContainer(nodeId=nodeId,datapath=datapath,_class='pbl_roundedGroup',border='1px solid gray',
                                    regions='^.controller.layoutregions')
        bc.data('.controller.layoutregions.left','215px',show=False)
        top = bc.contentPane(region='top',background='gray',_class='pbl_roundedGroupLabel')
        self.tt_bottom(bc.contentPane(region='bottom',datapath='.controller',_class='pbl_roundedGroupBottom'),wkdlist)
        self.tt_left(bc.borderContainer(region='left',datapath='.controller.conf',border_right='1px solid gray'),wkdlist)
        center = bc.contentPane(region='center')
        self.lazyContent(center,'ttdh_main',nodeId=nodeId,tstart=tstart,tstop=tstop,period=period,
                        wkdlist=wkdlist,series=series,fired=fired)


    def tt_left(self,bc,wkdlist):
        center = bc.contentPane(region='center')
        self.tt_colorPaletteMenu(center)

        fb = center.formbuilder(cols=1, border_spacing='2px',datapath='.dayrow.day')
        weekdays = dates.get_day_names(width='wide', locale=self.locale.replace('-','_'))
        for k in wkdlist:
            fb.div(background='^.color',lbl=weekdays[k],datapath='.%i'%k,border='1px solid black',baseClass='no_background',
                    height='12px',width='12px',connectedMenu='tt_colorPaletteMenu')
        
        fb = center.formbuilder(cols=1, border_spacing='2px',width='80%')
        fb.textbox(value='^.day.height',lbl='!!Height',width='100%')
        fb.textbox(value='^.day.background_color',lbl='!!Color',width='100%')
        
    def tt_bottom(self,bottom,wkdlist):
        bottom.horizontalSlider(value='^.zoom', minimum=.2, maximum=3,
                                intermediateChanges=True,width='15em',float='right')
        bottom.data('.zoom',1)         
        btn = bottom.button('!!Configuration',action='SET .layoutregions.left?show=!GET .layoutregions.left?show',
                            float='left')
        fb = bottom.formbuilder(cols=7, border_spacing='2px',datapath='.dayrow.day')
        weekdays = dates.get_day_names(width='wide', locale=self.locale.replace('-','_'))
        for k in wkdlist:
            fb.checkbox(value='^.show', default_value=True,label=weekdays[k],datapath='.%i' %k)
            
    def remote_ttdh_main(self,pane,tstart=None,tstop=None,period=None,wkdlist=None,fired=None,nodeId=None,series=None):
        self.tt_pars = dict(tstart=tstart,tstop=tstop,period=period,wkdlist=wkdlist,nodeId=nodeId,series=series)
        if hasattr(self,'tt_%s_onstart' %nodeId):
            getattr(self,'tt_%s_onstart' %nodeId)()
        days = self.tt_periodSlots()
        ttbox = pane.div(zoomFactor='^.controller.zoom')
        for j,dayrow in enumerate(days):
            day = dayrow['day']
            dataserie = dayrow['dataserie']
            row = ttbox.div(_class='dayrow dayrow_w%i' %day.weekday())
            self.tt_daylabel(row.div(width='^.controller.conf.weekday.width',default_width='70px',**rect(top=0,bottom=0,left=0)),day)
            #self.tt_daycontent(row.div(left='^.controller.conf.weekday.width',**rect(top=0,bottom=0,right=0)),dataserie)
            
    def tt_daylabel(self,cell=None,day=None):
        if hasattr(self,'tt_%s_daylabel' %self.tt_pars['nodeId']):
            return getattr(self,'tt_%s_daylabel' %self.tt_pars['nodeId'])(cell,day=day)
        pane = cell.div(_class='dayLabel',**rect(top=1,bottom=1,left=1,right=1))
        pane.div(toText(day,format='eeee',locale=self.locale),_class='dayLabel_WD WD_%i' %day.weekday())
        pane.div(toText(day,format='d',locale=self.locale),_class='dayLabel_D')
        pane.div(toText(day,format='MMMM',locale=self.locale),_class='dayLabel_M')
    
    def tt_daycontent(self,cell,dataserie,**kwargs):
        pane = cell.div(_class='dayContent',**rect(top=1,bottom=1,left=1,right=1))
        #sh = day_h/len(dataserie)
        minute_w = 6
        sh = 30
        start_hour = self.tt_pars['tstart'].hour
        for ns,ks in enumerate(dataserie.items()):
            s_top=ns*sh 
            key,slots=ks
            serierow = pane.div(**rect(left=0,top=s_top,height=sh))
            for slot in slots:
                left = ((slot['ts'].hour-start_hour)*60+slot['ts'].minute)*minute_w
                width = slot['minutes'] *minute_w
                slotcell = serierow.div(**rect(top=1,left=left+1,bottom=1,width=width-1))
                #_class='ttslot %s' %status,
                self.tt_slot(slotcell,slot=slot,width=width,height=sh)
            
    def tt_periodSlots(self):
        #wkdlist = [int(k) for k,v in wkdlist.items() if v] or None
        result = []
        series = self.tt_pars['series']
        provider_handler = getattr(self,'tt_%s_dataProvider' %self.tt_pars['nodeId'])
        for day in dayIterator(self.tt_pars['period'],locale=self.locale,workdate=self.workdate,wkdlist=self.tt_pars['wkdlist']):
            dataserie = dict()
            for serie in series:
                print serie
                r =  provider_handler(day=day,serie=serie)
                print r
                dataserie[serie['code']] = r
            result.append(dict(dataserie=dataserie,day=day))
        return result
                
    def tt_slot(self,cell=None,**kwargs):
        getattr(self,'tt_%s_slot' %self.tt_pars['nodeId'])(cell,**kwargs)
        
    def tt_localcss(self):
        return """
        .dayrow{
            height: 50px;
            position: relative;
            border-bottom: 1px solid gray;
        }
        .dayrow_bg_0{
            background-color: rgba(250,250,250,0.72);
        }

        .dayrow_bg_1{
            background-color: rgba(240,240,240,0.72);
        }
        .dayrow_bg_2{
            background-color: rgba(230,230,230,0.72);
        }
        .dayrow_bg_3{
            background-color: rgba(220,220,220,0.72);
        }
        .dayrow_bg_4{
            background-color: rgba(210,210,210,0.72);
        }
        
        .dayrow_bg_5{
            background-color: rgba(200,200,200,0.72);
        }
        .dayrow_bg_6{
            background-color: rgba(190,190,190,0.72);
        }
        

        
        
        
        
        
        
        
        """