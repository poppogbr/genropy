#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage import BaseComponent
import gnr.app.gnrbatch
from gnr.core.gnrlang import gnrImport


class BatchRunner(BaseComponent):
    
    def buildBatchRunner(self, pane, resultpath='aux.cmd', 
                         selectionName=None,selectedRowidx=None,recordId=None, 
                         fired=None, batch_class=None,
                         thermoParams=None, endScript=None,stopOnError=False, forUpdate=False, onRow=None, **kwargs):
        """Prepare a batch action on the maintable with a thermometer
           @param resultpath: the path into the datastore where the result is stored.
           @param fired: the path where you fire the event that launch the dataRpc of selectionBatchRunner.
           @param batchFactory: is used instead of rpc. Name of the Factory Class, used as
                                plugin of table, which executes the standard batch action.
           @param rpc: is used instead of batchFactory. The name of the custum rpc you can use for the batch
                       for every selected row.
        """
            
        
        thermoParams = thermoParams or dict()
        thermoid = None
        if 'field' in thermoParams:
            thermoid = self.getUuid()
            self.thermoDialog(pane, thermoid=thermoid, title=thermoParams.get('title', 'Batch Running'),
                            thermolines=thermoParams.get('lines',1), fired='^.openthermo', alertResult=True)
        pane.dataRpc('%s.result' % resultpath, 'runBatch', timeout=0, _POST=True,
                     table=kwargs.pop('table', self.maintable), selectionName=selectionName,
                     recordId = recordId,
                     batch_class=batch_class,
                     thermofield=thermoParams.get('field'), thermoid = thermoid,
                     selectedRowidx =selectedRowidx,
                     _fired=fired, _onResult=endScript,
                     forUpdate=forUpdate, _onCalling='FIRE .openthermo',**kwargs)
        dlgid = self.getUuid()
        pane.dataController('genro.wdgById(dlgid).show()', _if='errors',
                            dlgid=dlgid, errors='^%s.errors' % resultpath)
        d = pane.dialog(nodeId=dlgid, title="!!Errors in batch execution", width='27em', height='27em')
        struct = self.newGridStruct()
        rows = struct.view().rows()
        rows.cell('caption',width='8em',name='!!Caption')
        rows.cell('error', name='!!Error')
        d.div(position='absolute', top='28px', right='4px',
            bottom='4px', left='4px').includedView(storepath='%s.errors' % resultpath, struct=struct)
            
    def rpc_runBatch(self, table, selectionName=None,recordId=None ,batch_class=None, 
                    selectedRowidx=None, forUpdate=False, **kwargs):
        """batchFactory: name of the Class, plugin of table, which executes the batch action
            thermoid:
            thermofield: the field of the main table to use for thermo display or * for record caption
            stopOnError: at the first error stop execution
            forUpdate: load records for update and commit at end (always use for writing batch)
            onRow: optional method to execute on each record in selection, use if no batchFactory is given
            """
        tblobj = self.db.table(table)  

        if recordId and recordId!='*':
            data = tblobj.record(pkey=recordId,ignoreMissing=True).output('bag')
        else:    
            data = self.unfreezeSelection(tblobj, selectionName)
            if selectedRowidx:
                if isinstance(selectedRowidx, basestring):
                    selectedRowidx = [int(x) for x  in selectedRowidx.split(',')]
                selectedRowidx = set(selectedRowidx)
                data.filter(lambda r: r['rowidx'] in selectedRowidx)
            
        batch_class = self.batch_loader(batch_class)
        if batch_class:
            batch = batch_class(data=data, table=table, page=self, thermocb=self.app.setThermo, **kwargs)
            return batch.run()
        else:
            raise Exception
        
    def batch_loader(self, batch_class):
        if ':' in batch_class:
            module_path, class_name = batch_class.split(':')
            module = gnrImport(module_path)
        else:
            class_name = batch_class
            module = gnr.app.gnrbatch
        return getattr(module,class_name,None)