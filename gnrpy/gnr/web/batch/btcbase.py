#!/usr/bin/env python
# encoding: utf-8
"""
gnrserverbatch.py

Created by Francesco Porcari on 2010-10-16.
Copyright (c) 2010 Softwell. All rights reserved.
"""

from gnr.core.gnrbag import Bag

class BaseResourceBatch(object):
    batch_prefix = 'BB'
    batch_thermo_lines = 'batch_steps,batch_main,ts_loop'
    batch_title = 'My Batch Title'
    batch_cancellable = True
    batch_delay = 0.5
    batch_note = None
    batch_steps = None #'foo,bar'
    dialog_height = '200px'
    dialog_width = '300px'
    virtual_columns = None

    def __init__(self, page=None, resource_table=None):
        self.page = page
        self.db = self.page.db
        self.tblobj = resource_table
        if self.tblobj:
            self.maintable = self.tblobj.fullname
        self.btc = self.page.btc
        self.results = Bag()
        self.records = dict()
        self.result_info = dict()
        self._pkeys = None

    def __call__(self, batch_note=None, **kwargs):
        parameters = kwargs['parameters']
        self.batch_parameters = parameters.asDict(True) if isinstance(parameters, Bag) else parameters or {}
        self.batch_note = batch_note or self.batch_parameters.get('batch_note')
        try:
            self.run()
            result, result_attr = self.result_handler()
            self.btc.batch_complete(result=result, result_attr=result_attr)
            #self.page.setInClientData('')
        except self.btc.exception_stopped:
            self.btc.batch_aborted()
        except Exception, e:
            if self.page.site.debug:
                raise
            else:
                try:
                    self.btc.batch_error(error=str(e))
                except Exception, e:
                    print e
                    raise

    def _pre_process(self):
        self.pre_process()

    def pre_process(self):
        pass

    def run(self):
        self.btc.batch_create(batch_id='%s_%s' % (self.batch_prefix, self.page.getUuid()),
                              title=self.batch_title,
                              cancellable=self.batch_cancellable,
                              delay=self.batch_delay,
                              note=self.batch_note)
        self._pre_process()
        if self.batch_steps:
            for step in self.btc.thermo_wrapper(self.batch_steps, 'btc_steps', message=self.get_step_caption,
                                                keep=True):
                step_handler = getattr(self, 'step_%s' % step)
                step_handler()
                for line_code in self.btc.line_codes[1:]:
                    self.btc.thermo_line_del(line_code)
        else:
            self.do()

    def storeResult(self, key, result, record=None, **info):
        self.results[key] = result
        self.records[key] = record
        self.result_info[key] = info

    def batchUpdate(self, updater=None, table=None, where=None, line_code=None, message=None, **kwargs ):
        table = table or self.page.maintable
        tblobj = self.db.table(table)

        if not where:
            where = '$%s IN:pkeys' % tblobj.pkey
            kwargs['pkeys'] = self.get_selection_pkeys()

        tblobj.batchUpdate(updater=updater, where=where,
                           _wrapper=self.btc.thermo_wrapper,
                           _wrapperKwargs=dict(line_code='date',
                                               message=message or self.get_record_caption,
                                               tblobj=tblobj), **kwargs)

    def result_handler(self):
        return 'Execution completed', dict()

    def get_step_caption(self, item, progress, maximum, **kwargs):
        step_handler = getattr(self, 'step_%s' % item)
        return step_handler.__doc__

    def get_record_caption(self, item, progress, maximum, tblobj=None, **kwargs):
        tblobj = tblobj or self.tblobj
        if tblobj:
            caption = '%s (%i/%i)' % (tblobj.recordCaption(item), progress, maximum)
        else:
            caption = '%i/%i' % (progress, maximum)
        return caption

    def do(self, **kwargs):
        """override me"""
        pass

    def defineSelection(self, selectionName=None, selectedRowidx=None, selectionFilterCb=None):
        self.selectionName = selectionName
        self.selectedRowidx = selectedRowidx
        self.selectionFilterCb = selectionFilterCb

    def get_selection(self, columns=None):
        selection = self.page.getUserSelection(selectionName=self.selectionName,
                                               selectedRowidx=self.selectedRowidx, filterCb=self.selectionFilterCb,
                                               columns=columns)
        return selection

    def get_records(self):
        pkeys = self.get_selection_pkeys()
        for pkey in pkeys:
            yield self.get_record(pkey)

    def get_record(self, pkey, virtual_columns=None):
        return self.tblobj.record(pkey=pkey, virtual_columns=self.virtual_columns).output('bag')

    def get_selection_pkeys(self):
        if self._pkeys is None:
            self._pkeys = self.get_selection().output('pkeylist')
        return self._pkeys

    #def rpc_selectionFilterCb(self,row):
    #    """override me"""
    #    return True

    def parameters_pane(self, pane, **kwargs):
        """Pass a ContentPane for adding forms to allow you to ask parameters to the clients"""
        pass
        