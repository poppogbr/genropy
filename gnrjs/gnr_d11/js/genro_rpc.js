/*
 *-*- coding: UTF-8 -*-
 *--------------------------------------------------------------------------
 * package       : Genro js - see LICENSE for details
 * module genro_rpc : Genro clientside module for remote calling remote methods
 * Copyright (c) : 2004 - 2007 Softwell sas - Milano
 * Written by    : Giovanni Porcari, Francesco Cavazzana
 *                 Saverio Porcari, Francesco Porcari
 *--------------------------------------------------------------------------
 *This library is free software; you can redistribute it and/or
 *modify it under the terms of the GNU Lesser General Public
 *License as published by the Free Software Foundation; either
 *version 2.1 of the License, or (at your option) any later version.

 *This library is distributed in the hope that it will be useful,
 *but WITHOUT ANY WARRANTY; without even the implied warranty of
 *MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 *Lesser General Public License for more details.

 *You should have received a copy of the GNU Lesser General Public
 *License along with this library; if not, write to the Free Software
 *Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
 */



//######################## genro  #########################
dojo.declare("gnr.GnrRemoteResolver", gnr.GnrBagResolver, {
    constructor: function(kwargs, isGetter, cacheTime) {
        this.xhrKwargs = {'handleAs': 'xml',
            'timeout': 50000,
            'load': 'resultHandler',
            'error': 'errorHandler',
            'sync': false,
            'preventCache': false
        };
        var k;
        for (k in this.xhrKwargs) {
            if (k in kwargs) {
                this.xhrKwargs[k] = objectPop(kwargs, k);
            }
        }
        this.xhrKwargs.load = dojo.hitch(this, this.xhrKwargs.load);
        this.xhrKwargs.error = dojo.hitch(this, this.xhrKwargs.error);
        this.httpMethod = objectPop(kwargs, 'httpMethod');
        this.onloading = null;
    },
    load: function (kwargs) {
        if (this.onloading) {
            this.onloading(kwargs);
        }
        var sync = this.xhrKwargs.sync;
        var result = genro.rpc._serverCall(kwargs, this.xhrKwargs, this.httpMethod);
        if (sync) {
            result.addCallback(function(value) {
                result = value;
            });
        }
        return result;
    },
    errorHandler: function(response, ioArgs) {
        return genro.rpc.errorHandler(response, ioArgs);
    },
    resultHandler: function(response, ioArgs) {
        if (response.documentElement.tagName == 'parsererror') {
            // We got an error parsing the XML response from the server
            debugger;
        }
        return genro.rpc.resultHandler(response, ioArgs, (this.updateAttr ? this._parentNode.attr : null));
    }
});

dojo.declare("gnr.GnrServerCaller", gnr.GnrBagResolver, {
    constructor: function(kwargs /*url, page_id, methodname, params*/) {
        alert("GnrServerCaller");
        if (typeof kwargs.params == 'string') {
            this.evaluate = 'this.params = ' + kwargs.params;
            this.params = {};
        } else {
            this.evaluate = null;
            this.params = kwargs.params;
        }
        this.methodname = kwargs.methodname;
        this.respars = kwargs.respars || {};
    },

    load: function (kwargs, cb) {
        if (this.evaluate) {
            eval(this.evaluate);
        }
        if (kwargs) {
            objectUpdate(this.params, kwargs);
        }
        return genro.rpc.remoteCall(this.methodname, this.params, this.respars.mode || 'bag', null, null, cb);
    }

});


dojo.declare("gnr.GnrRpcHandler", null, {

    constructor: function(application) {
        this.application = application;
        this.counter = 0;
        this.rpc_register = {};
        this.rpc_counter = 0;
        this.rpc_level = 0;

    },
    register_call:function(kw) {
        this.rpc_counter = this.rpc_counter + 1;
        this.rpc_level = this.rpc_level + 1;
        kw['__rpc_counter'] = this.rpc_counter;
        this.rpc_register['r_' + this.rpc_counter] = kw;
        //console.log('rpc level:'+this.rpc_level)
    },
    unregister_call:function(ioArgs) {
        this.rpc_level = this.rpc_level - 1;
        var rpc_counter = ioArgs.args['__rpc_counter'];
        delete this.rpc_register['r_' + rpc_counter];
    },

    /* callbackArgs 
     args: Object
     the original object argument to the IO call.
     xhr: XMLHttpRequest
     For XMLHttpRequest calls only, the
     XMLHttpRequest object that was used for the
     request.
     url: String
     The final URL used for the call. Many times it
     will be different than the original args.url
     value.
     query: String
     For non-GET requests, the
     name1=value1&name2=value2 parameters sent up in
     the request.
     handleAs: String
     The final indicator on how the response will be
     handled.
     id: String
     For dojo.io.script calls only, the internal
     script ID used for the request.
     canDelete: Boolean
     For dojo.io.script calls only, indicates
     whether the script tag that represents the
     request can be deleted after callbacks have
     been called. Used internally to know when
     cleanup can happen on JSONP-type requests.
     json: Object
     For dojo.io.script calls only: holds the JSON
     response for JSONP-type requests. Used
     internally to hold on to the JSON responses.
     You should not need to access it directly --
     the same object should be passed to the success
     callbacks directly.

     */
    serverCall:function(callKwargs, xhrKwargs, httpMethod) {

    },
    _serverCall:function(callKwargs, xhrKwargs, httpMethod) {
        // s=serverCall({method:'moltiplica', op1:3, op2:7},{timeout:300,handleAs'xml',load=function(){}}
        /* 
         callKwargs :       The parameters for the server call. For genropy webpage
         it should include also the method to call.
         Remaining parameters should be jsonable so, for example, a bag should
         be converted to xml before this call.

         xhrKwargs  :       Object with original dojo parameters
         url - URL to server endpoint.
         content - Object : Contains properties with string values. These
         properties will be serialized as name1=value2 and
         passed in the request.
         timeout - Integer : Milliseconds to wait for the response. If this time
         passes, the then error callbacks are called.
         preventCache - Boolean : Default is false. If true, then a
         "dojo.preventCache" parameter is sent in the request
         with a value that changes with each request
         (timestamp). Useful only with GET-type requests.
         handleAs - String : Acceptable values depend on the type of IO
         transport (see specific IO calls for more information).
         load - Function : function(response, ioArgs){}. response is an Object, ioArgs
         is of type callbackArgs. The load function will be
         called on a successful response.
         error - Function : function(response, ioArgs){}. response is an Object, ioArgs
         is of type callbackArgs. The error function will
         be called in an error case.
         handle - Function : function(response, ioArgs){}. response is an Object, ioArgs
         is of type callbackArgs. The handle function will
         be called in either the successful or error case.
         sync - Boolean. false is default. Indicates whether the request should
         be a synchronous (blocking) request.
         headers - Object. Additional HTTP headers to send in the request.

         */
        var httpMethod = httpMethod || 'GET';
        if (genro._serverstore_changes) {
            callKwargs._serverstore_changes = genro._serverstore_changes;
            genro._serverstore_changes = null;
        }
        ;
        var delayOnCall = objectPop(callKwargs, '_delayOnCall');
        callKwargs = this.serializeParameters(genro.src.dynamicParameters(callKwargs));
        objectPop(callKwargs, '_destFullpath');
        callKwargs._lastUserEventTs = asTypedTxt(genro._lastUserEventTs, 'DH');
        if (genro.auto_polling > 0) {
            this._call_auto_polling();
        }
        var content = objectUpdate({}, callKwargs);
        content.page_id = this.application.page_id;
        var kw = objectUpdate({}, xhrKwargs);
        kw.url = kw.url || this.pageIndexUrl();

        if (this.application.debugopt) {
            content.debugopt = this.application.debugopt;
            content.callcounter = this.application.getCounter();
        }
        kw.content = content;
        //kw.preventCache = kw.preventCache - just to remember that we can have it
        kw.handleAs = kw.handleAs || 'xml';
        this.register_call(kw);
        var xhrResult;
        genro.lastRpc = new Date();
        if (genro.debugRpc) {
            this.debugRpc(kw);
        }
        ;
        if (delayOnCall) {
            //add this stuff to handle it
        } else {
            var deferred= this._serverCall_execute(httpMethod, kw, callKwargs);
            return deferred;
        }

    },
    _serverCall_execute: function(httpMethod, kw, callKwargs) {
        if (httpMethod == 'GET') {
            xhrResult = dojo.xhrGet(kw);
        }
        else if (httpMethod == 'POST') {
            if ('postData' in callKwargs) {
                xhrResult = dojo.rawXhrPost(kw);
            } else {
                xhrResult = dojo.xhrPost(kw);
            }
        }
        else if (httpMethod == 'DELETE') {
            xhrResult = dojo.xhrDelete(kw);
        }
        else if ('PUT') {
            if ('putData' in callKwargs) {
                xhrResult = dojo.rawXhrPut(kw);
            } else {
                xhrResult = dojo.xhrPut(kw);
            }
        }
        return xhrResult;
    },
    _call_auto_polling:function() {
        if (this._auto_polling_handler) {
            clearTimeout(this._auto_polling_handler);
        }
        this._auto_polling_handler = setTimeout(function() {
            genro.rpc.ping({reason:'auto'});
        }, genro.auto_polling * 1000);
    },
    setPolling:function(auto_polling, user_polling) {
        genro.user_polling = user_polling == null ? genro._('gnr.polling.user_polling') : user_polling;
        auto_polling = auto_polling == null ? genro._('gnr.polling.auto_polling') : auto_polling;
        if (auto_polling != genro.auto_polling) {
            genro.auto_polling = auto_polling;
            this._call_auto_polling();
        }
        ;
    },
    debugRpc:function(kw) {
        var method = kw.content ? kw.content.method : '';
        method = method == 'resolverRecall' ? method + ' : ' + kw.content.resolverPars : method;
        console.log('method:' + method + ' sync:' + kw.sync);
        console.log(kw);
    },
    errorCallback:function(type, errObj) {
        alert("errorCallback");

        var status = errObj.xhr.status;
        if (status = 200) {// it was a server error that created a traceback
            alert('there was a server error');
        }
        else if (status = 401) {
            genro.pageReload();
        }
        else {
            genro.iobindError = status;
        }
    },
    remoteCallAsync:function(method, params, async_cb) {
        alert("remoteCallAsync");
        return this.remoteCall(method, params, null, null, null, async_cb);
    },

    downloadCall: function(method, kwargs) {
        var cb = function(result) {
            genro.download(result);
        };
        genro.rpc.remoteCall(method, objectUpdate(kwargs, {'mode':'text'}), null, 'POST', null, cb);
    },
    remoteCall:function(method, params, mode, httpMethod, preventCache, async_cb) {
        var callKwargs = objectUpdate({}, params);
        callKwargs.method = method;
        var mode = mode || 'bag';
        var preprocessor, handleAs, result;
        if ((mode == 'bag') || (mode == 'xml')) {
            handleAs = 'xml';
            preprocessor = dojo.hitch(this, 'resultHandler');
        }
        else {
            handleAs = mode;
            preprocessor = function(response, ioArgs) {
                return response;
            };
        }
        var cb;
        var sync = objectPop(callKwargs, 'sync', false);
        if (async_cb) {
            cb = dojo.hitch(this, function(response, ioArgs) {
                var result = preprocessor(response, ioArgs);
                var error = (result && typeof(result) == 'object') ? result.error : null;
                try {
                    async_cb(result, error);
                } catch(e) {
                    console.error(e);
                    throw e;
                }
                return result;
            });
            //sync = false;
        } else {
            cb = dojo.hitch(this, function(response, ioArgs) {
                ioArgs.syncresult = preprocessor(response, ioArgs);
            });
            sync = true;
        }
        var timeout = objectPop(callKwargs, 'timeout', 50000);
        var xhrKwargs = {'handleAs': handleAs,
            'timeout': timeout,
            'load': cb,
            'error': dojo.hitch(this, 'errorHandler'),
            'sync': sync,
            'preventCache': preventCache
        };
        var deferred = this._serverCall(callKwargs, xhrKwargs, httpMethod);        
        return sync? deferred.ioArgs.syncresult:deferred;
    },
    errorHandler: function(response, ioArgs) {
        genro.dev.handleRpcHttpError(response, ioArgs);
    },
    setDatachangesInData:function (datachanges) {
        //console.log('apply datachanges');
        var changenodes = datachanges.getNodes();
        for (var i = 0; i < changenodes.length; i++) {
            var changenode = changenodes[i];
            var value = changenode.getValue();
            var attr = objectExtract(changenode.attr, 'change_*');
            var isDelete = objectPop(attr, 'delete');
            var changepath = attr.path;
            var fired = attr.fired;
            var reason = attr.reason;
            var change_ts = attr.ts;
            attr = attr.attr || {};
            attr._change_ts = change_ts;
            var updater = function(path, value, attr, reason) {
                if (genro._data.getItem(path) != value) {
                    genro._data.setItem(path, value, attr, reason != null ? {'doTrigger':reason,_updattr:true} : null);
                }
            };
            if (reason == 'serverChange') {
                for (var clientpath_prefix in genro._serverstore_paths) {
                    var serverpath_prefix = genro._serverstore_paths[clientpath_prefix];
                    if (stringStartsWith(changepath, serverpath_prefix)) {
                        clientpath = clientpath_prefix + changepath.slice(serverpath_prefix.length);
                        updater(clientpath, value, attr, reason);
                    }
                }
            }
            else if (isDelete) {
                genro._data.delItem(changepath);
            }
            else {
                updater(changepath, value, attr, reason);
                if (fired) {
                    genro._data.setItem(changepath, null, null, {'doTrigger':false});
                }
            }
        }
        ;
    },
    resultHandler: function(response, ioArgs, currentAttr) {
        this.unregister_call(ioArgs);
        var envelope = new gnr.GnrBag();
        try {
            envelope.fromXmlDoc(response, genro.clsdict);
        }
        catch(e) {
            console.log('error in fromXmlDoc');
            console.log(response);
            return;
        }
        var envNode = envelope.getNode('result');
        var resultAsNode = (envelope.getItem('resultType') == 'node') || currentAttr;
        var changenode,attr,value, changepath,serverpath, as_fired,reason;
        var datachanges = envelope.getItem('dataChanges');
        if (datachanges) {
            genro.rpc.setDatachangesInData(datachanges);
        }
        var error = envelope.getItem('error');
        if (!error) {
            var locStatus = envelope.getItem('_localizerStatus');
            if (locStatus) {
                genro.setLocStatus(locStatus);
            }
            if (currentAttr) {
                var attr = objectUpdate({}, currentAttr);
                if (!envNode) {
                    console.log(envNode);
                    debugger;
                }
                envNode.attr = objectUpdate(attr, envNode.attr);
            }
        } else {
            setTimeout(dojo.hitch(genro.dev, 'handleRpcError', error, envNode));
            return {'error':error};
        }
        if (resultAsNode) {
            return envNode;
        } else {
            if (envNode == null) {
                debugger;
            }
            return envNode.getValue();
        }

    },

    getRecordCount:function(field, value, cb) {
        var result = genro.rpc.remoteCall('app.getRecordCount', {'field':field, 'value':value}, null, 'GET', null, cb);
        return result;
    },

    pageIndexUrl:function() {
        return document.location.pathname;
    },


    remoteResolver: function(methodname, params, kw /*readOnly, cacheTime*/) {
        var kw = kw || {};
        var cacheTime = kw.cacheTime || -1;
        var isGetter = kw.isGetter || null;

        var kwargs = objectUpdate({'sync':true}, params);
        kwargs.method = methodname;

        var resolver = new gnr.GnrRemoteResolver(kwargs, isGetter, cacheTime);
        return resolver;
    },


    getURLParams: function(source) {
        if (source == null) {
            source = window.location.search;
        }
        var result = {};
        source.replace(/(?:[\?&])?([^=]+)=([^&]+)/g, function(str, key, value) {
            result[key] = unescape(value);
        });
        return result;
    },

    updateUrlParams: function(params, source) {
        return dojo.io.argsFromMap(objectUpdate(genro.rpc.getURLParams(source), params, true));
    },
    getRpcUrlArgs:function(method, kwargs, sourceNode, avoidCache) {
        var avoidCache = avoidCache === false ? false : true;
        var currParams = {};
        currParams['page_id'] = this.application.page_id;
        currParams['method'] = method;
        currParams['mode'] = 'text';
        if (avoidCache != false) {
            currParams['_no_cache_'] = genro.getCounter();
        }
        return objectUpdate(currParams, this.serializeParameters(genro.src.dynamicParameters(kwargs, sourceNode)));
    }
    ,
    rpcUrl:function(method, kwargs, sourceNode, avoidCache) {
        return genro.absoluteUrl(null, genro.rpc.getRpcUrlArgs(method, kwargs, sourceNode, avoidCache), avoidCache);
    },

    makoUrl:function(template, kwargs) {
        this.counter = this.counter + 1;
        var currParams = {};
        currParams['page_id'] = this.application.page_id;
        currParams['mako'] = template;
        currParams['_no_cache_'] = this.counter;
        objectUpdate(currParams, kwargs);
        var parameters = [];
        for (var key in currParams) {
            parameters.push(key + '=' + escape(currParams[key]));
        }
        return this.application.absoluteUrl('?' + parameters.join('&'));
    },

    serializeParameters: function(kwargs) {
        var cntrlstr = [];
        var currarg, nodeattrs;
        for (var attr in kwargs) {
            currarg = kwargs[attr];
            if ((currarg instanceof gnr.GnrBag) && (currarg.getParentNode() != null)) {
                nodeattrs = currarg.getParentNode().getAttr();
                if (objectNotEmpty(nodeattrs)) {
                    kwargs[attr + '_attr'] = asTypedTxt(nodeattrs);
                }
            }
            kwargs[attr] = asTypedTxt(currarg);
            cntrlstr.push(attr + '_' + kwargs[attr]);
        }
        return kwargs;
    },
    
    addDeferredCb:function(deferred,func,cblocals,sourceNode){
        if(sourceNode){
            var cblocals = sourceNode.evaluateOnNode(cblocals);
        }
        var isErrBack = objectPop(cblocals,'_isErrBack');
        var cb = function(result){
            cblocals['result'] = result;
            var newresult = funcApply(func, cblocals, sourceNode);
            return  newresult===undefined? result:newresult;
        }
        if(isErrBack){
            deferred.addErrback(cb);
        }else{
            deferred.addCallback(cb);
        }
    },
    
    
    ping:function(kw) {
        if (genro.pollingRunning) {
            return;
        }
        var kw = kw || {reason:null};
        genro.rpc.setPollingStatus(true);
        var xhrKwargs = {'handleAs':'xml',
            'url' :'http://' + document.location.host + '/_ping',
            'timeout': 10000,
            'load': dojo.hitch(this, function(response, ioArgs) {
                var result = genro.rpc.resultHandler(response, ioArgs);
                genro.rpc.setPollingStatus(false);
                return result;
            }),
            'error': dojo.hitch(this, function(response, ioArgs) {
                genro.rpc.errorHandler(response, ioArgs);
                genro.rpc.setPollingStatus(false);
            }),
            'sync': false,
            'preventCache': false
        };
        this._serverCall({page_id:genro.page_id,reason:kw.reason,_no_cache_:genro.getCounter()}, xhrKwargs, 'GET');
    },
    setPollingStatus:function(status) {
        genro.pollingRunning = status;
    },

    remote_relOneResolver: function(params, parentbag) {
        var kw = {};
        var cacheTime = -1;
        var isGetter = false;
        var sync = ('sync' in params) ? objectPop(params, 'sync') : true;
        var kwargs = { 'sync':sync,'from_fld':params._from_fld,
            'target_fld':params._target_fld,
            'sqlContextName':params._sqlContextName,
            'virtual_columns':params._virtual_columns};
        kwargs.method = 'app.getRelatedRecord';

        var resolver = new gnr.GnrRemoteResolver(kwargs, isGetter, cacheTime);
        resolver.updateAttr = true;
        resolver.onloading = function(kwargs) {
            var target = kwargs.target_fld.split('.');
            var table = target[0] + '_' + target[1];
            var loadingParameters = genro.getData('gnr.tables.' + table + '.loadingParameters');
            var rowLoadingParameters = objectPop(kwargs, 'rowLoadingParameters');
            if (rowLoadingParameters) {
                loadingParameters = loadingParameters || new gnr.GnrBag();
                var nodes = rowLoadingParameters.getNodes();
                for (var i = 0; i < nodes.length; i++) {
                    if (nodes[i].label[0] != '@') {
                        loadingParameters.setItem(nodes[i].label, nodes[i].getValue(), nodes[i].attr);
                    }
                }
                ;
            }
            kwargs['loadingParameters'] = loadingParameters;
        };
        var _related_field = params._target_fld.split('.')[2];

        if (params._auto_relation_value) {
            resolver.relation_fld = params._auto_relation_value; //params._from_fld.split('.')[2];
            var dataprovider = function() {
                return this.getParentNode().getParentBag().getItem(this.relation_fld);
            };
            kwargs[_related_field] = dojo.hitch(resolver, dataprovider);

            //TODO: move that feature to BagNode.setResolver
            var valNode = parentbag.getNode(resolver.relation_fld);
            var reloader = function() {
                this.getParentNode().getValue('reload');
            };
            valNode._onChangedValue = dojo.hitch(resolver, reloader);

        } else {
            kwargs[_related_field] = params._relation_value;
        }
        return resolver;
    },
    remote_relManyResolver: function(params) {
        var kw = {};
        var cacheTime = -1;
        var isGetter = false;

        var kwargs = {'sync':true,
            'columns':'==gnr.getGridColumns(_destFullpath);',
            'from_fld':params._from_fld, 'target_fld':params._target_fld, 'relation_value':params._relation_value,
            'sqlContextName':params._sqlContextName,order_by:params.many_order_by};
        
        kwargs.method = 'app.getRelatedSelection';

        var resolver = new gnr.GnrRemoteResolver(kwargs, isGetter, cacheTime);
        resolver.updateAttr = true;
        resolver.onSetResolver = function(node) {
            node.newBagRow = function(defaultArgs) {
                var childResolverParams = this.attr.childResolverParams;
                var table = childResolverParams._target_fld.split('.').slice(0, 2).join('_');
                var loadingParameters = genro.getData('gnr.tables.' + table + '.loadingParameters');
                if (defaultArgs instanceof Array) {

                } else {
                    //var defaultArgs = defaultArgs || {};
                    var resolver = genro.getRelationResolver(objectUpdate(childResolverParams, {'sync':true}));
                    if (!defaultArgs) {

                    }
                    resolver.kwargs.rowLoadingParameters = new gnr.GnrBag(defaultArgs);

                    var attr = objectUpdate({}, childResolverParams);
                    for (var label in defaultArgs) {
                        attr[label.replace(/\W/g, '_')] = defaultArgs[label];
                    }
                    ;
                    if (loadingParameters) {
                        var nodes = loadingParameters.getNodes();
                        for (var i = 0; i < nodes.length; i++) {
                            var n = nodes[i];
                            attr[n.label] = n.getValue();
                        }
                        ;
                    }
                    var result = new gnr.GnrBagNode(null, 'label', null, attr, resolver);
                    //result.getValue();
                    return result;
                }
            };
        };
        resolver.updateAttr = true;
        return resolver;
    },

    uploadMultipartFiles: function(filebag, kw) {
        var kw = kw || {};
        var uploaderId = kw.uploaderId;
        var onFileUploaded = kw.onFileUploaded || function() {
            genro.publish(uploaderId + '_done', arguments);
        };
        kw.onProgress = kw.onProgress || function() {
            genro.publish(uploaderId + '_progress', arguments);
        };
        kw.onError = kw.onError || function() {
            genro.publish(uploaderId + '_error', arguments);
        };
        kw.onAbort = kw.onAbort || function() {
            genro.publish(uploaderId + '_upload_aborted', arguments);
        };

        var onUploaded = function(node) {
            onFileUploaded(node);
            filebag.pop(node.label);
            genro.rpc.uploadMultipartFiles(filebag, kw);
        };
        var setProgress = function(statusNode, evt) {
            if (statusNode.last_execution_time && (new Date() - statusNode.last_execution_time < 500)) {
                return;
            }
            var percentComplete = '';
            if (evt.lengthComputable) {
                percentComplete = 100 * dojo.number.round(evt.loaded / evt.total, 2);
                percentComplete += ' %';
            }
            statusNode.attr.loaded = evt.loaded;
            statusNode.attr.total = evt.total;
            var message = 'SENDING: ' + percentComplete;
            kw.onProgress(statusNode, evt);
            statusNode.setValue(message);
            statusNode.last_execution_time = new Date();
            genro.upload_progress = null;
        };
        if (filebag.len() > 0) {
            var firstNode = filebag.getNode('#0');
            var statusNode = firstNode.getValue().getNode('_status', false, true);
            var params = firstNode.getValue().asObj();
            var file = objectPop(params, '_file');
            objectExtract(params, '_*');
            var innerKw = objectUpdate({}, kw);
            innerKw.onResult = function (e) {
                onUploaded(firstNode);
            };
            innerKw.onProgress = function (e) {
                setProgress(statusNode, e);
            };
            genro.rpc.uploadMultipart_oneFile(file, params, innerKw);
        } else {
            if (kw.onResult) {
                kw.onResult();
            }
        }
    },

    uploadMultipart_oneFile:function(file, params, kw) {
        params = params || {};
        var paramValue = function(param, value) {
            param.push('');
            param.push(value);
            param.push('');
            return param.join(_crlf);
        };
        var textParam = function(name, value) {
            var param = [];
            param.push('Content-Disposition: form-data; name="' + name + '"');
            param.push('Content-Type: text/plain');
            return paramValue(param, value);
        };
        var fileParam = function(filedata) {
            var param = [];
            param.push('Content-Disposition: form-data; name="file_handle"; filename="' + file['name'] + '"');
            param.push('Content-Type: application/octet-stream');
            return paramValue(param, file.getAsBinary());
        };
        var addContentLength = function(content) {
            return "Content-Length: " + content.length + _crlf + _crlf + content;
        };
        var content = [];
        content.push('');
        params['rpc'] = kw.method || 'rpc.upload_file';
        params['page_id'] = genro.page_id;
        params['uploaderId'] = kw.uploaderId;
        params['uploadPath'] = kw.uploadPath;

        var sourceNode = kw.uploaderId ? genro.nodeById(kw.uploaderId) : null;
        params = this.serializeParameters(genro.src.dynamicParameters(params, sourceNode));
        for (key in params) {
            content.push(textParam(key, params[key]));
        }
        var boundary = '------multipartformboundary' + (new Date).getTime();
        var sender = new XMLHttpRequest();
        var errorCb = function() {
            console.log(arguments);
        };
        if (kw.onResult) sender.upload.addEventListener("load", kw.onResult, false);
        if (kw.onProgress) sender.upload.addEventListener("progress", kw.onProgress, false);
        if (kw.onError) sender.upload.addEventListener("error", kw.onError || errorCb, false);
        if (kw.onAbort) sender.upload.addEventListener("abort", kw.onAbort, false);
        var filereader = new FileReader();
        var sendData = function() {
            content.push(fileParam(filereader.result));
            content = content.join('--' + boundary + _crlf) + boundary + '--' + _crlf;
            content = addContentLength(content);
            sender.open("POST", genro.rpc.pageIndexUrl(), true);
            sender.setRequestHeader("Content-Type", 'multipart/form-data; boundary=' + boundary);
            sender.sendAsBinary(content);
        };

        filereader.addEventListener("loadend", sendData, false);
        filereader.readAsBinaryString(file);
    }
});