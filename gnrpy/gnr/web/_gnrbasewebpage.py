# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package           : GenroPy web - see LICENSE for details
# module gnrwebcore : core module for genropy web framework
# Copyright (c)     : 2004 - 2007 Softwell sas - Milano 
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

#_gnrbasewebpage.py

#Created by Giovanni Porcari on 2007-03-24.
#Copyright (c) 2007 Softwell. All rights reserved.

import os
import sys
import time
import traceback
import urllib

import logging

gnrlogger = logging.getLogger(__name__)

try:
    import json
except:
    import simplejson as json

from gnr.core.gnrbag import Bag, TraceBackResolver

from gnr.core.gnrlang import GnrObject
from gnr.core.gnrstring import  toJson
from gnr.core import gnrdate

from gnr.sql.gnrsql_exceptions import GnrSqlSaveException, GnrSqlDeleteException

AUTH_OK = 0
AUTH_NOT_LOGGED = 1
AUTH_FORBIDDEN = -1

class GnrWebClientError(Exception):
    pass
    
class GnrWebServerError(Exception):
    pass
    
class GnrBaseWebPage(GnrObject):
    """add???"""
    def newCookie(self, name, value, **kw):
        """add???
        
        :param name: add???
        :param value: add???
        :returns: add???
        """
        return self.request.newCookie(name, value, **kw)
        
    def newMarshalCookie(self, name, value, secret=None, **kw):
        """add???
        
        :param name: add???
        :param value: add???
        :param secret: add???. Default value is ``None``
        :returns: add???
        """
        return self.request.newMarshalCookie(name, value, secret=secret, **kw)
        
    def get_cookie(self, cookieName, cookieType, secret=None, path=None):
        """add???
        
        :param cookieName: add???
        :param cookieType: add???
        :param secret: add???. Default value is ``None``
        :param path: add???. Default value is ``None``
        :returns: add???
        """
        return self.request.get_cookie(cookieName, cookieType,
                                       secret=secret, path=path)
                                       
    def add_cookie(self, cookie):
        """add???
        
        :param cookie: add???
        """
        self.response.add_cookie(cookie)
        
    def _get_clientContext(self):
        cookie = self.get_cookie('genroContext', 'simple')
        if cookie:
            return Bag(urllib.unquote(cookie.value))
        else:
            return Bag()
            
    def _set_clientContext(self, bag):
        value = urllib.quote(bag.toXml())
        cookie = self.get_cookie('genroContext', 'simple', path=self.site.default_uri)
        cookie.value = value
        self.add_cookie(cookie)
        
    clientContext = property(_get_clientContext, _set_clientContext)
        
    def _get_filename(self):
        try:
            return self._filename
        except AttributeError:
            self._filename = os.path.basename(self.filepath)
            return self._filename
            
    filename = property(_get_filename)
        
    def _get_canonical_filename(self):
        return self.filename
        
    canonical_filename = property(_get_canonical_filename)
        
    def rpc_decodeDatePeriod(self, datestr, workdate=None, locale=None):
        """add???
        
        :param datestr: add???
        :param workdate: add???. Default value is ``None``
        :param locale: add???. Default value is ``None``
        :returns: add???
        """
        workdate = workdate or self.workdate
        locale = locale or self.locale
        period = datestr
        valid = False
        try:
            returnDate = gnrdate.decodeDatePeriod(datestr, workdate=workdate, locale=locale, returnDate=True)
            valid = True
        except:
            returnDate = (None, None)
            period = None
        result = Bag()
        result['from'] = returnDate[0]
        result['to'] = returnDate[1]
        result['prev_from'] = gnrdate.dateLastYear(returnDate[0])
        result['prev_to'] = gnrdate.dateLastYear(returnDate[1])
        result['period'] = period
        result['valid'] = valid
        result['period_string'] = gnrdate.periodCaption(locale=locale, *returnDate)
        return result
        
    def mixins(self):
        """Implement this method in your page for mixin the page with methods from the local _resources folder
        
        :returns: a list of mixin names, moduleName:className
        """
        return []
        
    def requestWrite(self, txt, encoding='utf-8'):
        """add???
        
        :param txt: add???
        :param encoding: add???. Default value is ``utf-8``
        """
        self.responseWrite(txt, encoding=encoding)
        
    def responseWrite(self, txt, encoding='utf-8'):
        """add???
        
        :param txt: add???
        :param encoding: add???. Default value is ``utf-8``
        """
        self.response.write(txt.encode(encoding))
        
    def _get_siteStatus(self):
        if not hasattr(self, '_siteStatus'):
            path = os.path.join(self.siteFolder, 'data', '_siteStatus.xml')
            
            if os.path.isfile(path):
                self._siteStatus = Bag(path)
            else:
                self._siteStatus = Bag()
        return self._siteStatus
        
    siteStatus = property(_get_siteStatus)
        
    def siteStatusSave(self):
        """add???"""
        if hasattr(self, '_siteStatus'):
            path = os.path.join(self.siteFolder, 'data', '_siteStatus.xml')
            self._siteStatus.toXml(path)
            
    def pageAuthTags(self, method=None, **kwargs):
        """Allow to define users authorizations
        
        :param method: add???. Default value is ``None``
        :returns: a string containing add???
        """
        return ""
        
    def pageLocalDocument(self, docname):
        """add???
        
        :param docname: add???
        :returns: add???
        """
        folder = os.path.join(self.connectionFolder, self.page_id)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        return os.path.join(folder, docname)
        
    def freezeSelection(self, selection, name):
        """add???
        
        :param selection: add???
        :param name: add???
        :returns: add???
        """
        path = self.pageLocalDocument(name)
        selection.freeze(path, autocreate=True)
        return path
        
    def unfreezeSelection(self, dbtable=None, name=None):
        """add???
        
        :param dbtable: add???. Default value is ``None``
        :param name: add???. Default value is ``None``
        :returns: add???
        """
        assert name, 'name is mandatory'
        if isinstance(dbtable, basestring):
            dbtable = self.db.table(dbtable)
        selection = self.db.unfreezeSelection(self.pageLocalDocument(name))
        if dbtable and selection is not None:
            assert dbtable == selection.dbtable, 'unfrozen selection does not belong to the given table'
        return selection
        
    def getUserSelection(self, selectionName=None, selectedRowidx=None, filterCb=None, columns=None,
                         condition=None, table=None, condition_args=None):
        """add???
        
        :param selectionName: add???. Default value is ``None``
        :param selectedRowidx: add???. Default value is ``None``
        :param filterCb: add???. Default value is ``None``
        :param columns: add???. Default value is ``None``
        :param condition: add???. Default value is ``None``
        :param table: add???. Default value is ``None``
        :param condition_args: add???. Default value is ``None``
        :returns: add???
        """
        # table is for checking if the selection belong to the table
        assert selectionName, 'selectionName is mandatory'
        if isinstance(table, basestring):
            table = self.db.table(table)
        selection = self.unfreezeSelection(dbtable=table, name=selectionName)
        table = table or selection.dbtable
        if filterCb:
            filterCb = getattr(self, 'rpc_%s' % filterCb)
            selection.filter(filterCb)
        elif selectedRowidx:
            if isinstance(selectedRowidx, basestring):
                selectedRowidx = [int(x) for x  in selectedRowidx.split(',')]
                selectedRowidx = set(selectedRowidx) #use uniquify (gnrlang) instead
            selection.filter(lambda r: r['rowidx'] in selectedRowidx)
        if columns:
            condition_args = condition_args or {}
            pkeys = selection.output('pkeylist')
            where = 't0.%s in :pkeys' % table.pkey
            if condition:
                where = '%s AND %s' % (where, condition)
            selection = table.query(columns=columns, where=where,
                                    pkeys=pkeys, addPkeyColumn=False,
                                    **condition_args).selection()
        return selection
        
    def getAbsoluteUrl(self, path, **kwargs):
        """Return an external link to the page
        
        :param path: the path to the page from 'pages' folder
        :returns: an external link to the page
        """
        return self.request.construct_url(self.getDomainUrl(path, **kwargs))
        
    def resolvePathAsUrl(self, *args, **kwargs):
        """add???
        
        :returns: add???
        """
        return self.diskPathToUri(self.resolvePath(*args, **kwargs))
        
    def resolvePath(self, *args, **kwargs):
        """add???
        
        :returns: add???
        """
        folder = kwargs.pop('folder', None)
        sitefolder = self.siteFolder
        if folder == '*data':
            diskpath = os.path.join(sitefolder, 'pages', '..', 'data', *args)
            return diskpath
        elif folder == '*users':
            diskpath = os.path.join(sitefolder, 'pages', '..', 'data', '_users', *args)
            return diskpath
        elif folder == '*home':
            diskpath = os.path.join(sitefolder, 'pages', '..', 'data', '_users', self.user, *args)
            return diskpath
        elif folder == '*pages':
            diskpath = os.path.join(sitefolder, 'pages', *args)
        elif folder == '*lib':
            diskpath = os.path.join(sitefolder, 'pages', '_lib', *args)
        elif folder == '*static':
            diskpath = os.path.join(sitefolder, 'pages', 'static', *args)
        else:
            diskpath = os.path.join(os.path.dirname(self.filename), *args)
        diskpath = os.path.normpath(diskpath)
        return diskpath
        
    def diskPathToUri(self, tofile, fromfile=None):
        """add???
        
        :param tofile: add???
        :param fromfile: add???. Default value is ``None``
        :returns: add???
        """
        fromfile = fromfile or self.filename
        pagesfolder = self.folders['pages']
        relUrl = tofile.replace(pagesfolder, '').lstrip('/')
        path = fromfile.replace(pagesfolder, '')
        rp = '../' * (len(path.split('/')) - 1)
        
        path_info = self.request.path_info
        if path_info: # != '/index'
            rp = rp + '../' * (len(path_info.split('/')) - 1)
        return '%s%s' % (rp, relUrl)
        
    def _get_siteName(self):
        return os.path.basename(self.siteFolder.rstrip('/'))
        
    siteName = property(_get_siteName)
        
    def _get_dbconnection(self):
        if not self._dbconnection:
            self._dbconnection = self.db.adapter.connect()
        return
        
    dbconnection = property(_get_dbconnection)
        
    def _get_packages(self):
        return self.db.packages
        
    packages = property(_get_packages)
        
    def _get_package(self):
        pkgId = self.packageId
        if pkgId:
            return self.db.package(pkgId)
            
    package = property(_get_package)
        
    def _get_tblobj(self):
        if self.maintable:
            return self.db.table(self.maintable)
            
    tblobj = property(_get_tblobj)
        
    def formSaver(self, formId, table=None, method=None, _fired='', datapath=None,
                  resultPath='dummy', changesOnly=True, onSaving=None, onSaved=None, saveAlways=False, **kwargs):
        """add???
        
        :param formId: add???
        :param table: add???. Default value is ``None``
        :param method: add???. Default value is ``None``
        :param _fired: add???. Default value is ``''``
        :param datapath: add???. Default value is ``None``
        :param resultPath: add???. Default value is ``None``
        :param changesOnly: boolean. add???. Default value is ``True``
        :param onSaving: add???. Default value is ``None``
        :param onSaved: add???. Default value is ``None``
        :param saveAlways: boolean. add???. Default value is ``False``
        """
        method = method or 'saveRecordCluster'
        controller = self.pageController()
        data = '==genro.getFormCluster("%s");'
        onSaved = onSaved or ''
        _onCalling = kwargs.pop('_onCalling', None)
        if onSaving:
            _onCalling = """var currform = genro.formById("%s");
                            var onSavingCb = function(record,form){%s};
                             %s
                            var result = onSavingCb.call(this, data.getItem('record'), currform);
                            if(result===false){
                                currform.status = null;
                                return false;
                            }else if(result instanceof gnr.GnrBag){
                                $1.data.setItem('record',result);
                            }""" % (formId, onSaving, _onCalling or '')
                            
        _onError = """var cb = function(){genro.formById("%s").status=null;};
                    genro.dlg.ask(kwargs._errorTitle,error,{"confirm":"Confirm"},
                                  {"confirm":cb});""" % formId
        if changesOnly:
            data = '==genro.getFormChanges("%s");'
        controller.dataController('genro.formById("%s").save(always)' % formId, _fired=_fired,
                                  datapath=datapath, always=saveAlways)
        kwargs['fireModifiers'] = _fired.replace('^', '=')
        controller.dataRpc(resultPath, method=method, nodeId='%s_saver' % formId, _POST=True,
                           datapath=datapath, data=data % formId, _onCalling=_onCalling,
                           _onResult='genro.formById("%s").saved();%s;' % (formId, onSaved),
                           _onError=_onError, _errorTitle='!!Saving error',
                           table=table, **kwargs)
                           
    def formLoader(self, formId, resultPath, table=None, pkey=None, datapath=None,
                   _fired=None, loadOnStart=False, lock=False,
                   method=None, onLoading=None, onLoaded=None, loadingParameters=None, **kwargs):
        """add???
        
        :param formId: add???
        :param resultPath: add???
        :param table: add???. Default value is ``None``
        :param pkey: add???. Default value is ``None``
        :param datapath: add???. Default value is ``None``
        :param _fired: add???. Default value is ``None``
        :param loadOnStart: boolean add???. Default value is ``False``
        :param lock: boolean. add???. Default value is ``False``
        :param method: add???. Default value is ``None``
        :param onLoading: add???. Default value is ``None``
        :param onLoaded: add???. Default value is ``None``
        :param loadingParameters: add???. Default value is ``None``
        """
        pkey = pkey or '*newrecord*'
        method = method or 'loadRecordCluster'
        onResultScripts = []
        onResultScripts.append('genro.formById("%s").loaded()' % formId)
        if onLoaded:
            onResultScripts.append(onLoaded)
        loadingParameters = loadingParameters or '=gnr.tables.maintable.loadingParameters'
        controller = self.pageController()
        controller.dataController('genro.formById(_formId).load();',
                                  _fired=_fired, _onStart=loadOnStart, _delay=1, _formId=formId,
                                  datapath=datapath)
                                  
        controller.dataRpc(resultPath, method=method, pkey=pkey, table=table,
                           nodeId='%s_loader' % formId, datapath=datapath, _onCalling=onLoading,
                           _onResult=';'.join(onResultScripts), lock=lock,
                           loadingParameters=loadingParameters,
                           virtual_columns='==genro.formById(_formId).getVirtualColumns()',
                           _formId=formId, **kwargs)
                           
    def rpc_loadRecordCluster(self, table=None, pkey=None, recordGetter='app.getRecord', **kwargs):
        """add???
        
        :param table: add???. Default value is ``None``
        :param pkey: add???. Default value is ``None``
        :param recordGetter: add???. Default value is ``app.getRecord``
        :returns: add???
        """
        table = table or self.maintable
        getterHandler = self.getPublicMethod('rpc', recordGetter)
        record, recinfo = getterHandler(table=table, pkey=pkey, **kwargs)
        return record, recinfo
        
    def rpc_saveRecordCluster(self, data, table=None, _nocommit=False, rowcaption=None, _autoreload=False, **kwargs):
        """add???
        
        :param data: add???
        :param table: add???. Default value is ``None``
        :param _nocommit: boolean. add???. Default value is ``False``
        :param rowcaption: add???. Default value is ``None``
        :param _autoreload: boolean. add???. Default value is ``False``
        :returns: add???
        """
        #resultAttr = None #todo define what we put into resultAttr
        resultAttr = {}
        onSavingMethod = 'onSaving'
        onSavedMethod = 'onSaved'
        maintable = getattr(self, 'maintable')
        table = table or maintable
        tblobj = self.db.table(table)
        if table != maintable:
            onSavingMethod = 'onSaving_%s' % table.replace('.', '_')
            onSavedMethod = 'onSaved_%s' % table.replace('.', '_')
        onSavingHandler = getattr(self, onSavingMethod, None)
        onSavedHandler = getattr(self, onSavedMethod, None)
        node = data.getNode('record')
        recordCluster = node.value
        recordClusterAttr = node.getAttr()
        onSavedKwargs = dict()
        if onSavingHandler:
            onSavedKwargs = onSavingHandler(recordCluster, recordClusterAttr, resultAttr=resultAttr) or {}
        virtual_columns = self.pageStore().getItem('tables.%s.virtual_columns' % table)
        if virtual_columns:
            for virtual_col in virtual_columns.keys():
                recordCluster.pop(virtual_col, None)
        record = tblobj.writeRecordCluster(recordCluster, recordClusterAttr)
        if onSavedHandler:
            onSavedHandler(record, resultAttr=resultAttr, **onSavedKwargs)
        if not _nocommit:
            self.db.commit()
        if not 'caption' in resultAttr:
            resultAttr['caption'] = tblobj.recordCaption(record, rowcaption=rowcaption)
        pkey = record[tblobj.pkey]
        if _autoreload:
            result = Bag()
            result.setItem('pkey',pkey,**resultAttr)
            keyToLoad=pkey if _autoreload  is  True else _autoreload
            record,recInfo = self.app.rpc_getRecord(pkey=keyToLoad,table=table)
            result.setItem('loadedRecord',record,**recInfo)
            return result
        else:
            return (pkey, resultAttr)
            
    def rpc_deleteRecordCluster(self, data, table=None, **kwargs):
        """add???
        
        :param data: add???
        :param table: add???. Default value is ``None``
        :returns: add???
        """
        maintable = getattr(self, 'maintable')
        table = table or maintable
        tblobj = self.db.table(table)
        node = data.getNode('record')
        recordCluster = node.value
        recordClusterAttr = node.getAttr()
        try: #try:
            self.onDeleting(recordCluster, recordClusterAttr)
            recordClusterAttr['_deleterecord'] = True
            record = tblobj.writeRecordCluster(recordCluster, recordClusterAttr)
            self.onDeleted(record)
            self.db.commit()
            return 'ok'
        except GnrSqlDeleteException, e:
            return ('delete_error', {'msg': e.message})
            
    def rpc_deleteDbRow(self, table, pkey=None, **kwargs):
        """Method for deleting a single record from a given tablename 
        and from a record or its pkey
        
        :param table: the table from which you want to delete a single record
        :param pkey: the table's primary key. Default value is ``None``
        :returns: if it works, returns the primary key and the deleted attribute.
                  Else, return an exception
        """
        try:
            tblobj = self.db.table(table)
            record = tblobj.record(pkey, for_update=True, mode='bag')
            deleteAttr = dict()
            self.onDeleting(record, deleteAttr)
            tblobj.delete(record)
            self.onDeleted(record)
            self.db.commit()
            return pkey, deleteAttr
        except GnrSqlDeleteException, e:
            return ('delete_error', {'msg': e.message})
            
    def setLoadingParameters(self, table, **kwargs):
        """add???
        
        :param table: add???
        """
        self.pageSource().dataFormula('gnr.tables.%s.loadingParameters' % table.replace('.', '_'),
                                      '', _onStart=True, **kwargs)
                                      
    def toJson(self, obj):
        """add???
        
        :param obj: add???
        :returns: add???
        """
        return toJson(obj)
        
    def setOnBeforeUnload(self, root, cb, msg):
        """add???
        
        :param root: add???
        :param cb: add???
        :param msg: add???
        """
        root.script("""genro.checkBeforeUnload = function(e){
                       if (%s){
                           return "%s";
                       }
                }""" % (cb, self._(msg)))
                
    def mainLeftContent(self, parentBC, **kwargs):
        pass
        
    def pageController(self, **kwargs):
        """add???
        
        :returns: add???
        """
        return self.pageSource().dataController(**kwargs)
        
    def pageSource(self, nodeId=None):
        """add???
        
        :param nodeId: add???
        :returns: add???
        """
        if nodeId:
            return self._root.nodeById(nodeId)
        else:
            return self._root
            
    def rootWidget(self, root, **kwargs):
        """add???
        
        :param root: add???
        :returns: add???
        """
        return root.contentPane(**kwargs)
        
    def main(self, root, **kwargs): #You MUST override this !
        """add???
        
        :param root: add???
        """
        root.h1('You MUST override this main method !!!')
        
    def forbiddenPage(self, root, **kwargs):
        """add???
        
        :param root: add???
        """
        dlg = root.dialog(toggle="fade", toggleDuration=250, onCreated='widget.show();')
        f = dlg.form()
        f.div(content='Forbidden Page', text_align="center", font_size='24pt')
        tbl = f.contentPane(_class='dojoDialogInner').table()
        row = tbl.tr()
        row.td(content='Sorry. You are not allowed to use this page.', align="center", font_size='16pt',
               color='#c90031')
        cell = tbl.tr().td()
        cell.div(float='right', padding='2px').button('Back', action='genro.pageBack()')
        
    def windowTitle(self):
        """Return the window title.
        
        :returns: the window title.
        """
        return os.path.splitext(os.path.basename(self.filename))[0].replace('_', ' ').capitalize()
        
    def _errorPage(self, err, method=None, kwargs=None):
        page = self.domSrcFactory.makeRoot(self)
        sc = page.stackContainer(height='80ex', width='50em', selected='^_dev.traceback.page')
        p1 = sc.contentPane(background_color='silver')
        #msc=sc.menu()
        #msc.menuline('Close traceback',action='genro.wdgById("traceback_main").hide()')
        p1.div(
                'Sorry: an error occurred on server while executing the method:<br> %s <br><br>Check parameters before executing again last command.' % method
                ,
                text_align='center', padding='1em', font_size='2em', color='gray', margin='auto')
        p1.button(label='See errors', action='FIRE _dev.traceback.page=1', position='absolute', bottom='1em',
                  right='1em')
        accordion = sc.accordionContainer()
        accordion.accordionPane(title='traceback').div(border='1px solid gray', background_color='silver', padding='5px'
                                                       , margin_top='3em').pre(traceback.format_exc())
        errBag = TraceBackResolver()()
        for k, tb in errBag.items():
            currpane = accordion.accordionPane(title=k)
            currpane.div(tb['line'], font_size='1.2em', margin='4px')
            tbl = currpane.table(_class='bagAttributesTable').tbody()
            for node in tb['locals'].nodes:
                v = node.getStaticValue()
                tr = tbl.tr()
                tr.td(node.label, align='right')
                try:
                    if not isinstance(v, basestring):
                        v = str(v)
                    if not isinstance(v, unicode):
                        v = v.decode('ascii', 'ignore')
                except:
                    v = 'unicode error'
                tr.td(v.encode('ascii', 'ignore'))
        return page
            
    def rpc_resolverRecall(self, resolverPars=None, **auxkwargs):
        """add???
        
        :param resolverPars: add???. Default value is ``None``
        :returns: add???
        """
        if isinstance(resolverPars, basestring):
            resolverPars = json.loads(resolverPars) #should never happen
        resolverclass = resolverPars['resolverclass']
        resolvermodule = resolverPars['resolvermodule']
        
        args = resolverPars['args'] or []
        kwargs = {}
        for k, v in (resolverPars['kwargs'] or {}).items():
            k = str(k)
            if k.startswith('_serialized_'):
                pool, k = k.replace('_serialized_', '').split('_')
                v = getattr(self, pool)[v]
            kwargs[k] = v
        kwargs.update(auxkwargs)
        self.response.content_type = "text/xml"
        resolverclass = str(resolverclass)
        resolver = None
        if resolverclass in globals():
            resolver = globals()[resolverclass](*args, **kwargs)
        else:
            resolver = getattr(sys.modules[resolvermodule], resolverclass)(*args, **kwargs)
        if resolver is not None:
            resolver._page = self
            return resolver()
            
    def rpc_resetApp(self, **kwargs):
        """add???"""
        self.siteStatus['resetTime'] = time.time()
        self.siteStatusSave()
        
    def rpc_applyChangesToDb(self, **kwargs):
        """add???
        
        :returns: add???
        """
        return self._checkDb(applychanges=True)
        
    def rpc_checkDb(self):
        """add???
        
        :returns: add???
        """
        return self._checkDb(applychanges=False)
        
    def _checkDb(self, applychanges=False, changePath=None, **kwargs):
        changes = self.db.checkDb()
        if applychanges:
            if changePath:
                changes = self.db.model.modelBagChanges.getAttr(changePath, 'changes')
                self.db.execute(changes)
            else:
                for x in self.db.model.modelChanges:
                    self.db.execute(x)
            self.db.commit()
            self.db.checkDb()
        return self.db.model.modelBagChanges
        
    def rpc_tableStatus(self, **kwargs):
        """add???
        
        :returns: add???
        """
        strbag = self._checkDb(applychanges=False)
        for pkgname, pkg in self.db.packages.items():
            for tablename in pkg.tables.keys():
                records = self.db.query('%s.%s' % (pkgname, tablename)).count()
                strbag.setAttr('%s.%s' % (pkgname, tablename), recordsnum=records)
        return strbag
        
    def createFileInData(self, *args):
        """add???
        
        :returns: add???
        """
        if args:
            path = os.path.join(self.siteFolder, 'data', *args)
            dirname = os.path.dirname(path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            outfile = file(path, 'w')
            return outfile
            
    def createFileInStatic(self, *args):
        """add???
        
        :returns: add???
        """
        if args:
            path = os.path.join(self.siteFolder, 'pages', 'static', *args)
            dirname = os.path.dirname(path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            outfile = file(path, 'w')
            return outfile
            
    def createFolderInData(self, *args):
        """add???
        
        :returns: add???
        """
        if args:
            path = os.path.join(self.siteFolder, 'data', *args)
            if not os.path.exists(path):
                os.makedirs(path)
            return path
            
    def createFolderInStatic(self, *args):
        """add???
        
        :returns: add???
        """
        if args:
            path = os.path.join(self.siteFolder, 'pages', 'static', *args)
            if not os.path.exists(path):
                os.makedirs(path)
            return path