//GNRWDG WIDGET DEFINITION BASE
dojo.declare("gnr.widgets.gnrwdg", null, {
    constructor: function(application) {
        this._domtag = 'div';
    },
    _beforeCreation: function(sourceNode) {
        sourceNode.gnrwdg = {'gnr':this,'sourceNode':sourceNode};
        var attributes = sourceNode.attr;
        sourceNode.attr = {};
        sourceNode.attr.tag=objectPop(attributes,'tag')
        var datapath=objectPop(attributes,'datapath')
        if(datapath){sourceNode.attr.datapath=datapath;}
        var contentKwargs = this.contentKwargs(sourceNode, attributes);
        if (!this.createContent) {
            return false;
        }
        sourceNode.freeze();
        var children = sourceNode.getValue();
        sourceNode.clearValue();
        var content = this.createContent(sourceNode, contentKwargs,children);
        content.concat(children);
        sourceNode._stripData(true);
        sourceNode.unfreeze(true);
        return false;
    },
    onStructChild:function(attributes) {
        if (!attributes.datapath) {
            var defaultDatapath = this.defaultDatapath(attributes);
            if (defaultDatapath) {
                attributes.datapath = defaultDatapath;
            }
        }

    },
    contentKwargs: function(sourceNode, attributes) {
        return attributes;
    },
    defaultDatapath:function(attributes) {
        return null;
    }
});

dojo.declare("gnr.widgets.Palette", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode, attributes) {
        var left = objectPop(attributes, 'left');
        var right = objectPop(attributes, 'right');
        var top = objectPop(attributes, 'top');
        var bottom = objectPop(attributes, 'bottom');
        if ((left === null) && (right === null) && (top === null) && (bottom === null)) {
            this._last_floating = this._last_floating || {top:0,right:0};
            this._last_floating['top'] += 10;
            this._last_floating['right'] += 10;
            top = this._last_floating['top'] + 'px';
            right = this._last_floating['right'] + 'px';
        }
        var dockTo = objectPop(attributes, 'dockTo');
        var floating_kwargs = objectUpdate(attributes, {dockable:true,closable:false,visibility:'hidden'});
        var showOnStart = false;
        if (dockTo === false) {
            floating_kwargs.closable = true;
            floating_kwargs.dockable = false;
            showOnStart = true;
        } else if (dockTo && dockTo.indexOf(':open') >= 0) {
            dockTo = dockTo.split(':')[0];
            objectPop(floating_kwargs, 'visibility');
            showOnStart = true;
        }
        if (showOnStart) {
            floating_kwargs.onCreated = function(widget) {
                setTimeout(function() {
                    widget.show();
                    widget.bringToTop();
                }, 1);
            };
        }
        if (!dockTo && dockTo !== false) {
            dockTo = 'default_dock';
        }
        if (dockTo) {
            floating_kwargs.dockTo = dockTo;
        }
        return objectUpdate({height:'400px',width:'300px',
            top:top,right:right,left:left,bottom:bottom,
            resizable:true}, floating_kwargs);
    },
    createContent:function(sourceNode, kw) {
        if (kw.dockTo == '*') {
            var dockId = sourceNode._id + '_dock';
            sourceNode._('dock', {id:dockId});
            kw.dockTo = dockId;
        }
        if (kw.nodeId) {
            var that=this;
            kw.connect_show = function() {
                genro.publish(kw.nodeId + '_showing');
            };
            kw.connect_hide = function() {
                genro.publish(kw.nodeId + '_hiding');
            };
        }
        return sourceNode._('floatingPane', kw);
    }
});

dojo.declare("gnr.widgets.PalettePane", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode, attributes) {
        var inattr = sourceNode.getInheritedAttributes();
        var groupCode = inattr.groupCode;
        attributes.nodeId = attributes.nodeId || 'palette_' + attributes.paletteCode;
        attributes._class = attributes._class || "basePalette";
        if (groupCode) {
            attributes.groupCode = groupCode;
            attributes.pageName = attributes.paletteCode;
        }
        return attributes;
    },

    defaultDatapath:function(attributes) {
        return  'gnr.palettes.' + attributes.paletteCode;
    },
    createContent:function(sourceNode, kw) {
        var paletteCode = objectPop(kw, 'paletteCode');
        var contentWidget = objectPop(kw,'contentWidget') || 'ContentPane';
        var groupCode = objectPop(kw, 'groupCode');
        if (groupCode) {
            var pane = sourceNode._('ContentPane', objectExtract(kw, 'title,pageName'))._(contentWidget, objectUpdate({'detachable':true}, kw));
            var controller_kw = {'script':"SET gnr.palettes._groups.pagename." + groupCode + " = paletteCode;",
                'paletteCode':paletteCode}
            controller_kw['subscribe_show_palette_' + paletteCode] = true;
            pane._('dataController', controller_kw);
            return pane;
        } else {
            var palette_kwargs = objectExtract(kw, 'title,dockTo,top,left,right,bottom,maxable,height,width');
            palette_kwargs['nodeId'] = paletteCode + '_floating';
            palette_kwargs['title'] = palette_kwargs['title'] || 'Palette ' + paletteCode;
            objectUpdate(palette_kwargs, objectExtract(kw, 'palette_*'));
            palette_kwargs.selfsubscribe_showing = function() {
                genro.publish('palette_' + paletteCode + '_showing');
            }
            palette_kwargs.selfsubscribe_hiding = function() {
                genro.publish('palette_' + paletteCode + '_hiding');
            }
            var floating = sourceNode._('palette', palette_kwargs);
            return floating._(contentWidget, kw);
        }
    }
});

dojo.declare("gnr.widgets.FramePane", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var node;
        var frameCode = kw.frameCode;
        genro.assert(frameCode,'Missing frameCode');
        var frameId = frameCode+'_frame';
        genro.assert(!genro.nodeById(frameId),'existing frame');
        sourceNode.attr.nodeId = frameId;
        sourceNode._registerNodeId();
        objectPop(kw,'datapath');
        var rounded_corners = genro.dom.normalizedRoundedCorners(kw.rounded,objectExtract(kw,'rounded_*',true))
        var centerPars = objectExtract(kw,'center_*');

        var bc = sourceNode._('BorderContainer', kw);
        var slot,v;
        var sides= kw.design=='sidebar'? ['left','right','top','bottom']:['top','bottom','left','right']
        var corners={'left':['top_left','bottom_left'],'right':['top_right','bottom_right'],'top':['top_left','top_right'],'bottom':['bottom_left','bottom_right']}
        dojo.forEach(sides,function(side){
             slot = children.popNode(side);
             node = slot? slot.getValue().getNode('#0') : children.popNode('#side='+side);
             if(node){                 
                 node.attr['frameCode'] = frameCode;
                 objectPop(node.attr,'side');
                 dojo.forEach(corners[side],function(c){
                     v=objectPop(rounded_corners,c)
                     if(v){
                         node.attr['rounded_'+c] = v;
                     }
                 })             
                 bc._('ContentPane',{'region':side}).setItem('#id',node._value,node.attr);
             }
        });
        slot = children.popNode('center');
        var centerNode = slot? slot.getValue().getNode('#0'):children.popNode('#side=center');
        var center;
        var rounded={};
        var frameChild;
        frameChild = children.popNode('#_frame=true::B');
        while(frameChild){
            objectPop(frameChild.attr,'_frame');
            bc.setItem(frameChild.label,frameChild._value,frameChild.attr);
            frameChild = children.popNode('#_frame=true::B');
        }
        
        for(var k in rounded_corners){
            rounded['rounded_'+k]=rounded_corners[k]
        }
        if(centerNode){
            objectPop(centerNode.attr,'side');
            centerNode.attr['region'] = 'center';
            bc.setItem('#id',centerNode._value,objectUpdate(rounded,centerNode.attr));
            center = centerNode._value;
        }else{
            centerPars['region'] = 'center';
            centerPars['widget'] = centerPars['widget'] || 'ContentPane'
            center = bc._(centerPars['widget'],objectUpdate(rounded,centerPars));
        }
        return center;
    }
});

dojo.declare("gnr.widgets.FrameForm", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var formId = objectPop(kw,'formId');
        var storeNode = children.popNode('formStore');
        var store = this.createStore(storeNode);
        var storepath = store.storepath;
        var frameCode = kw.frameCode;
        formId = formId || frameCode+'_form';
        var frame = sourceNode._('FramePane',objectUpdate({controllerPath:'.controller',formDatapath:storepath,pkeyPath:'.pkey',formId:formId,form_store:store},kw));
        if(kw.hasBottomMessage!==false){
            frame._('SlotBar',{'side':'bottom',slots:'*,messageBox,*',_class:'fh_bottom_message',messageBox_subscribeTo:'form_'+formId+'_message'});
        }
        var storeId = kw.store+'_store';
        var centerPars = objectExtract(kw,'center_*');
        centerPars['widget'] = objectPop(centerPars,'widget') || 'ContentPane';
        frame._(centerPars['widget'],objectUpdate({side:'center','_class':'fh_content','nodeId':formId+'_content',datapath:storepath},centerPars));
        return frame;
    },
    createStore:function(storeNode){
        var storeCode = storeNode.attr.storeCode;
        storeNode.attr.storepath = storeNode.attr.storepath || '.record';
        var storeContent = storeNode.getValue();
        var action,callbacks;
        storeNode._value = null;
        var handlers = {};
        if(storeContent){
            storeContent.forEach(function(n){
                action = objectPop(n.attr,'action');
                if(action){
                    objectPop(n.attr,'tag');
                    handlers[action] = n.attr;
                    callbacks = n.getValue();
                    if(callbacks){
                        handlers[action]['callbacks'] = callbacks;
                    }
                }
            });
        }        
        var kw = storeNode.attr;
        var storeType = objectPop(kw,'storeType');
        storeType = storeType ||(kw.parentStore?'Collection':'Item');
        return new gnr.formstores[storeType](kw,handlers);
    }
});


dojo.declare("gnr.widgets.PaletteGrid", gnr.widgets.gnrwdg, {
    contentKwargs:function(sourceNode, attributes){
        var gridId = attributes.gridId || attributes.paletteCode+'_grid';
        attributes['frameCode'] = attributes.paletteCode;
        var reloadOnShow = objectPop(attributes,'reloadOnShow');
        attributes.selfsubscribe_showing = function() {
            var grid = genro.wdgById(gridId);
            if (grid.storebag().len() == 0 || reloadOnShow==true) {
                grid.reload();
            }
        }
        return attributes;
    },
    createContent:function(sourceNode, kw,children) {
        var frameCode = kw.frameCode;
        var gridId = objectPop(kw, 'gridId') || frameCode+'_grid';
        var storepath = objectPop(kw, 'storepath');
        var structpath = objectPop(kw, 'structpath');
        var store = objectPop(kw, 'store');
        var _newGrid = objectPop(kw,'_newGrid');
        var paletteCode=kw.paletteCode
        structpath = structpath? sourceNode.absDatapath(structpath):'.struct';
        var gridKwargs = {'nodeId':gridId,'datapath':'.grid',
                           'table':objectPop(kw,'table'),
                           'margin':'6px','configurable':true,
                           'structpath': structpath,
                           'frameCode':frameCode,
                           'autoWidth':false,
                           'store':store,
                           'relativeWorkspace':true};   
        gridKwargs.onDrag = function(dragValues, dragInfo) {
            if (dragInfo.dragmode == 'row') {
                dragValues[paletteCode] = dragValues.gridrow.rowset;
            }
        };     
        gridKwargs.draggable_row=true;
        objectUpdate(gridKwargs, objectExtract(kw, 'grid_*'));
        
        kw['contentWidget'] = 'FramePane';
        var pane = sourceNode._('PalettePane',kw)
        if(kw.searchOn){
            pane._('SlotBar',{'side':'top',slots:'*,searchOn',searchOn:objectPop(kw,'searchOn'),toolbar:true});
        }
        
        pane._(_newGrid?'NewIncludedView':'includedview', gridKwargs);
        return pane;
    }    
});

dojo.declare("gnr.widgets.PaletteTree", gnr.widgets.gnrwdg, {
    contentKwargs:function(sourceNode, attributes){
        attributes['frameCode'] = attributes.paletteCode;
        attributes.tree_onDrag = function(dragValues, dragInfo, treeItem) {
            if (treeItem.attr.child_count && treeItem.attr.child_count > 0) {
                return false;
            }
            dragValues['text/plain'] = treeItem.attr.caption;
            dragValues[attributes.paletteCode] = treeItem.attr;
        };
        attributes.tree_draggable=true;
        return attributes;
    },

    createContent:function(sourceNode, kw) {
        var frameCode = kw.frameCode;
        var editable = objectPop(kw, 'editable');
        var treeId = objectPop(kw, 'treeId') || frameCode + '_tree';
        var storepath = objectPop(kw, 'storepath') || '.store';
        var tree_kwargs = {_class:'fieldsTree', hideValues:true,
                            margin:'6px',nodeId:treeId,
                            'frameCode':frameCode,
                            storepath:storepath,labelAttribute:'caption'};
        objectUpdate(tree_kwargs, objectExtract(kw, 'tree_*'));
        var searchOn = objectPop(kw, 'searchOn');
        kw['contentWidget'] = 'FramePane';
        var pane = sourceNode._('PalettePane',kw);
        if (searchOn) {
            pane._('SlotBar',{'side':'top',slots:'*,searchOn',searchOn:true,toolbar:true});
        }
        if (editable) {
            var bc = pane._('BorderContainer',{'side':'center'});
            var bottom = bc._('ContentPane', {'region':'bottom',height:'30%',
                splitter:true});
            bottom._('BagNodeEditor', {nodeId:treeId + '_editbagbox',datapath:'.bagNodeEditor',bagpath:pane.getParentNode().absDatapath(storepath)});
            pane = bc._('ContentPane',{'region':'center'});
        }
        pane._('tree', tree_kwargs);
        return pane;
    }
});

dojo.declare("gnr.widgets.PaletteBagNodeEditor", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw) {
        var nodeId = objectPop(kw, 'nodeId');
        var pane = sourceNode._('PalettePane', kw);
        pane._('BagNodeEditor', {nodeId:nodeId,datapath:'.bagNodeEditor',bagpath:kw.bagpath});
        return pane;
    }
});

dojo.declare("gnr.widgets.BagNodeEditor", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw) {
        var gnrwdg = sourceNode.gnrwdg;
        var nodeId = objectPop(kw, 'nodeId');
        var readOnly = objectPop(kw, 'readOnly', false);
        var valuePath = objectPop(kw, 'valuePath');
        var showBreadcrumb = objectPop(kw, 'showBreadcrumb', true);
        var bc = sourceNode._('BorderContainer', {'nodeId':nodeId,detachable:true,_class:'bagNodeEditor'});
        if (showBreadcrumb) {
            var top = bc._('ContentPane', {'region':'top',background_color:'navy',color:'white'});
            top._('span', {'innerHTML':'Path : '});
            top._('span', {'innerHTML':'^.currentEditPath'});
        }
        var box = bc._('ContentPane', {'region':'center',_class:'formgrid'});
        var gridId = nodeId + '_grid';
        var topic = nodeId + '_editnode';
        var bagpath = objectPop(kw, 'bagpath');
        this.prepareStruct();
        gnrwdg.bagpath = bagpath;
        gnrwdg.valuePath = valuePath;
        gnrwdg.readOnly = readOnly;
        dojo.subscribe(topic, this, function(item) {
            gnrwdg.gnr.setCurrentNode(gnrwdg, item)
        });
        var grid = box._('includedview', {'storepath':'.data','structpath':'gnr._dev.bagNodeEditorStruct',
            'datamode':'bag','relativeWorkspace':true,'nodeId':gridId,
            autoWidth:false,'editorEnabled':true});
        if (!readOnly) {
            var gridEditor = grid._('gridEditor');
            var cellattr = {'gridcell':'attr_value','autoWdg':true};
            cellattr.validate_onAccept = function(value, result, validations, rowIndex, userChange) {
                var dataNode = this.grid.storebag().getParentNode().attr.dataNode;
                var attr_name = this.getRelativeData('.attr_name');
                if (attr_name == '*value') {
                    dataNode.setValue(value);
                } else {
                    var newattr = !('attr_name' in dataNode.attr);
                    dataNode.setAttribute(attr_name, value);
                    if (!value) {
                        objectPop(dataNode.attr, attr_name);
                    }
                    if (newattr || !value)
                        setTimeout(function() {
                            genro.publish(topic, dataNode);
                        }, 300);
                }
            };
            gridEditor._('textbox', {gridcell:'attr_name'});
            gridEditor._('textbox', cellattr);
        }
        return box;
    },
    setCurrentNode:function(gnrwdg, item) {
        var bagpath = gnrwdg.bagpath;
        var sourceNode = gnrwdg.sourceNode;
        if (typeof(item) == 'string') {
            item = sourceNode.getRelativeData(bagpath).getNode(item);
        }
        var itempath = item.getFullpath(null, sourceNode.getRelativeData(bagpath));
        sourceNode.setRelativeData('.currentEditPath', itempath);
        gnrwdg.currentEditPath = itempath;
        var newstore = new gnr.GnrBag();
        for (var k in item.attr) {
            var row = new gnr.GnrBag();
            row.setItem('attr_name', k, {_editable:false});
            row.setItem('attr_value', item.attr[k]);
            newstore.setItem('#id', row);
        }
        var itemvalue = item.getValue('static');

        if (gnrwdg.valuePath) {
            sourceNode.setRelativeData(gnrwdg.valuePath, itemvalue);
        } else {
            var editable = true;
            row = new gnr.GnrBag();
            row.setItem('attr_name', '*value', {_editable:false});
            if (itemvalue instanceof gnr.GnrBag) {
                var editable = false;
                itemvalue = '*bag*';
            }
            row.setItem('attr_value', itemvalue, {_editable:editable});
            newstore.setItem('#id', row);
        }

        newstore.sort('attr_name');
        //newstore.forEach(function(n){if(n.label.indexOf('~~')==0){n.label=n.label.slice(2);}});
        if (!gnrwdg.readOnly) {
            newstore.setItem('#id', new gnr.GnrBag({'attr_name':null,'attr_value':null}));
        }
        sourceNode.setRelativeData('.data', newstore, {'dataNode':item});
    },
    prepareStruct:function() {
        if (genro.getData('gnr._dev.bagNodeEditorStruct')) {
            return;
        }
        var rowstruct = new gnr.GnrBag();
        rowstruct.setItem('cell_0', null, {field:'attr_name',name:'Name',width:'30%',
            cellStyles:'background:gray;color:white;border-bottom:1px solid white;'});
        rowstruct.setItem('cell_1', null, {field:'attr_value',name:'Value',width:'70%',
            cellStyles:'border-bottom:1px solid lightgray;'});
        genro.setData('gnr._dev.bagNodeEditorStruct.view_0.row_0', rowstruct);
    }
});

dojo.declare("gnr.widgets.SearchBox", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode, attributes) {
        //var topic = attributes.nodeId+'_keyUp';
        var delay = 'delay' in attributes ? objectPop(attributes, 'delay') : 100;
        attributes.onKeyUp = function(e) {
            var sourceNode = e.target.sourceNode;
            if (sourceNode._onKeyUpCb) {
                clearTimeout(sourceNode._onKeyUpCb);
            }
            var v = e.target.value;
            sourceNode._onKeyUpCb = setTimeout(function() {
                sourceNode.setRelativeData('.currentValue', v);
            }, delay);
        };
        return attributes;
    },
    defaultDatapath:function(attributes) {
        return '.searchbox';
    },
    createContent:function(sourceNode, kw) {
        var searchOn = objectPop(kw, 'searchOn') || true;
        var searchDtypes;
        if (searchOn[0] == '*') {
            searchDtypes = searchOn.slice(1);
            searchOn = true;
        }
        var nodeId = objectPop(kw, 'nodeId');
        var menubag;
        var databag = new gnr.GnrBag();
        var defaultLabel = objectPop(kw, 'searchLabel') || 'Search';
        databag.setItem('menu_dtypes', searchDtypes);
        databag.setItem('caption', defaultLabel);
        this._prepareSearchBoxMenu(searchOn, databag);
        sourceNode.setRelativeData(null, databag);
        var searchbox = sourceNode._('table', {nodeId:nodeId,width:'100%'})._('tbody')._('tr');
        sourceNode._('dataController', {'script':'genro.publish(searchBoxId+"_changedValue",currentValue,field)',
            'searchBoxId':nodeId,currentValue:'^.currentValue',field:'^.field'});
        var searchlbl = searchbox._('td');
        searchlbl._('div', {'innerHTML':'^.caption',_class:'buttonIcon'});
        searchlbl._('menu', {'modifiers':'*',_class:'smallmenu',storepath:'.menubag',
            selected_col:'.field',selected_caption:'.caption'});
        
        searchbox._('td')._('div',{_class:'searchInputBox'})._('input', {'value':'^.value',connect_onkeyup:kw.onKeyUp});
        dojo.subscribe(nodeId + '_updmenu', this, function(searchOn) {
            menubag = this._prepareSearchBoxMenu(searchOn, databag);
        });
        return searchbox;
    },
    _prepareSearchBoxMenu: function(searchOn, databag) {
        var menubag = new gnr.GnrBag();
        var i = 0;
        if (searchOn === true) {
            databag.setItem('menu_auto', menubag);
        }
        else {
            dojo.forEach(searchOn.split(','), function(col) {
                col = dojo.trim(col);
                var caption = col;
                if (col.indexOf(':') >= 0) {
                    col = col.split(':');
                    caption = col[0];
                    col = col[1];
                }
                col = col.replace(/[.@]/g, '_');
                menubag.setItem('r_' + i, null, {col:col,caption:caption,child:''});
                i++;
            });
        }
        databag.setItem('field', menubag.getItem('#0?col'));
        var defaultLabel = menubag.getItem('#0?caption');
        if (defaultLabel) {
            databag.setItem('caption', defaultLabel);
        }
        databag.setItem('menubag', menubag);
        databag.setItem('value', '');
    }

});


dojo.declare("gnr.widgets.PaletteGroup", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw) {
        var groupCode = objectPop(kw, 'groupCode');
        var palette_kwargs = objectExtract(kw, 'title,dockTo,top,left,right,bottom');
        palette_kwargs['nodeId'] = palette_kwargs['nodeId'] || groupCode + '_floating';
        palette_kwargs.selfsubscribe_showing = function() {
            genro.publish('palette_' + this.getRelativeData('gnr.palettes._groups.pagename.' + groupCode) + '_showing'); //gnr.palettes?gruppopiero=palettemario
        }
        palette_kwargs['title'] = palette_kwargs['title'] || 'Palette ' + groupCode;
        var floating = sourceNode._('palette', palette_kwargs);
        var tab_kwargs = objectUpdate(kw, {selectedPage:'^gnr.palettes._groups.pagename.' + groupCode,groupCode:groupCode,_class:'smallTabs'});
        var tc = floating._('tabContainer', tab_kwargs);
        return tc;
    }
});


dojo.declare("gnr.widgets.SlotButton", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var slotbarCode = sourceNode.getInheritedAttributes().slotbarCode;
        var target = kw.target || sourceNode.getInheritedAttributes().target;
        kw['showLabel'] = kw.iconClass? (kw['showLabel'] || false):true;        
        var topic = (target || slotbarCode)+'_'+objectPop(kw,'publish');
        if(!kw.action){
            kw.topic = topic;
            kw.command = kw.command || null;
            kw.opt = objectExtract(kw,'opt_*');
            kw['action'] = "genro.publish(topic,{'command':command,modifiers:genro.dom.getEventModifiers(event),opt:opt})";
        }
        return sourceNode._('button',kw);
    }

});


dojo.declare("gnr.widgets.SlotBar", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode, attributes) {
        var frameNode = sourceNode.getParentNode().getParentNode();
        var side=sourceNode.getParentNode().attr.region;
        var framePars = frameNode.attr;
        var sidePars = objectExtract(framePars,'side_*',true);
        var orientation = attributes.orientation || 'horizontal';
        if (side){
            orientation = ((side=='top')||(side=='bottom'))?'horizontal':'vertical';
        }
        attributes.orientation=orientation
        var buildKw={}
        dojo.forEach(['table','row','cell','lbl'],function(k){
            buildKw[k] = objectExtract(attributes,k+'_*');
            buildKw[k]['_class'] = (buildKw[k]['_class'] || '') + ' slotbar_'+k;
        });
        
        if(orientation=='horizontal'){
            if('height' in attributes){
                buildKw.cell['height']= objectPop(attributes,'height');
            }
        }else{
            if('width' in attributes){
                buildKw.cell['width'] = objectPop(attributes,'width');
            }
        }
        attributes['_class'] = (attributes['_class'] || '')+' slotbar  slotbar_'+orientation+' slotbar_'+side
        var toolbar = objectPop(attributes,'toolbar');
        if(toolbar===true){
            toolbar = 'top';
        }
        side = side || toolbar;
        if(side){
            attributes['side'] = side;
            attributes['slotbarCode'] = attributes['slotbarCode'] || attributes['frameCode'] +'_'+ side; 
            if(toolbar){
                attributes['_class'] += ' slotbar_toolbar';
                attributes['gradient_from'] = attributes['gradient_from'] || sidePars['gradient_from'] || genro.dom.themeAttribute('toolbar','gradient_from','silver');
                attributes['gradient_to'] = attributes['gradient_to'] || sidePars['gradient_to'] || genro.dom.themeAttribute('toolbar','gradient_to','whitesmoke');
                
                var css3Kw = {'left':[0,'right'],'top':[-90,'bottom'],
                            'right':[180,'left'],'bottom':[90,'top']}
                attributes['border_'+css3Kw[side][1]] = '1px solid '+ attributes['gradient_from'];
                attributes['gradient_deg'] = css3Kw[side][0];
            }
        }
        buildKw.lbl['_class'] = buildKw.lbl['_class'] || 'slotbar_lbl'
        buildKw.lbl_cell = objectExtract(buildKw.lbl,'cell_*');
        attributes['buildKw'] = buildKw;
        return attributes;
    },
    
    createContent:function(sourceNode, kw,children) {
        var slots = objectPop(kw,'slots');
        return this['createContent_'+objectPop(kw,'orientation')](sourceNode,kw,kw.slotbarCode,slots,children);
    },
    createContent_horizontal:function(sourceNode,kw,slotbarCode,slots,children){
        var buildKw = objectPop(kw,'buildKw');
        var lblPos = objectPop(buildKw.lbl,'position') || 'N';
        var table = sourceNode._('div',kw)._('table',buildKw.table)._('tbody');
        var rlabel;
        if(lblPos=='T'){
            rlabel=  table._('tr');
        }
        var r = table._('tr',buildKw.row);
        if(lblPos=='B'){
            rlabel=  table._('tr');
        }
        var attr,cell,slotNode,slotValue,slotKw,slotValue;
        var children = children || new gnr.GnrBag();
        var that = this;
        var attr,kwLbl,lbl,labelCell,k;
        var slotArray = splitStrip(slots);
        var counterSpacer = dojo.filter(slotArray,function(s){return s=='*'}).length;
        var spacerWidth = counterSpacer? 100/counterSpacer:100;
        var cellKwLbl = buildKw.lbl_cell;
        dojo.forEach(slotArray,function(slot){
            if(rlabel){
                labelCell = rlabel._('td',cellKwLbl);
            }else if(lblPos=='L'){
                cellKwLbl['width'] = cellKwLbl['width'] || '1px'
                labelCell = r._('td',cellKwLbl)
            }
            if(slot=='*'){
                r._('td',{'_class':'slotbar_elastic_spacer',width:spacerWidth+'%'});
                return;
            }
            if(slot==parseInt(slot)){
                r._('td')._('div',{width:slot+'px'});
                return;
            }
            if(slot=='|'){
                r._('td')._('div',{_class:'slotbar_spacer'});
                return;
            }
            cell = r._('td',objectUpdate({_slotname:slot},buildKw.cell));
            if(lblPos=='R'){
                cellKwLbl['width'] = cellKwLbl['width'] || '1px';
                labelCell = r._('td',cellKwLbl)
            }
            slotNode = children.popNode(slot);
            if (!that['slot_'+slot] && slotNode){
                if(slotNode.attr.tag=='slot'){
                    slotValue = slotNode.getValue();
                }else{
                    slotValue = new gnr.GnrBag({'slot':slotNode});
                }
                if(slotValue instanceof gnr.GnrBag){
                    k=0;
                    slotValue.forEach(function(n){
                        attr = n.attr;
                        kwLbl = objectExtract(attr,'lbl_*');
                        lbl = objectPop(attr,'lbl');
                        cell.setItem(n.label,n._value,n.attr);
                        if((k==0)&&labelCell){
                            kwLbl = objectUpdate(objectUpdate({},buildKw.lbl),kwLbl);
                            labelCell._('div',objectUpdate({'innerHTML':lbl,'text_align':'center'},kwLbl));
                        }
                        k++;
                    })
                }
            }
            if(cell.len()==0){
                if(that['slot_'+slot]){
                    slotKw = objectExtract(kw,slot+'_*');
                    slotValue = objectPop(kw,slot);
                    lbl = objectPop(slotKw,'lbl');
                    kwLbl = objectExtract(slotKw,'lbl_*');
                    kwLbl = objectUpdate(objectUpdate({},buildKw.lbl),kwLbl);
                    that['slot_'+slot](cell,slotValue,slotKw,kw.frameCode)
                    if(labelCell){
                        labelCell._('div',objectUpdate({'innerHTML':lbl,'text_align':'center'},kwLbl));
                    }
                }else{
                    var textSlot=kw[slot]?kw[slot]:slot;
                    if(textSlot){
                        cell.setItem('div_0',null,objectUpdate({innerHTML:textSlot,tag:'div'},objectExtract(kw,slot+'_*')));
                    }
                }
            }       
        });
        
        return r;
    },
    createContent_vertical:function(sourceNode,kw,slotbarCode,slots,children){
        var buildKw = objectPop(kw,'buildKw');
        var lblPos = objectPop(buildKw.lbl,'position') || 'N';
        var table = sourceNode._('div',kw)._('table',buildKw.table)._('tbody');

        var attr,cell,slotNode,slotValue,slotKw,slotValue;
        var children = children || new gnr.GnrBag();
        var that = this;
        var attr,kwLbl,lbl,labelCell,k;
        var slotArray = splitStrip(slots);
        var cellKwLbl = buildKw.lbl_cell;
        dojo.forEach(slotArray,function(slot){
            /*if(rlabel){
                labelCell = rlabel._('td',cellKwLbl);
            }else if(lblPos=='L'){
                cellKwLbl['width'] = cellKwLbl['width'] || '1px'
                labelCell = r._('td',cellKwLbl)
            }*/
            if(slot=='*'){
                table._('tr');
                return;
            }
            if(slot=='|'){
                table._('tr',{'height':'1px'})._('td')._('div',{_class:'slotbar_spacer'});
                return;
            }
            if(slot==parseInt(slot)){
                table._('tr',{height:slot+'px'});
                return;
            }
            
            cell = table._('tr',buildKw.row)._('td',objectUpdate({_slotname:slot},buildKw.cell));
            /*if(lblPos=='R'){
                cellKwLbl['width'] = cellKwLbl['width'] || '1px';
                labelCell = r._('td',cellKwLbl)
            }*/
            slotNode = children.popNode(slot);
            if (slotNode){
                slotValue = slotNode.getValue();
                if(slotValue instanceof gnr.GnrBag){
                    k=0;
                    slotValue.forEach(function(n){
                        attr = n.attr;
                        kwLbl = objectExtract(attr,'lbl_*');
                        lbl = objectPop(attr,'lbl');
                        cell.setItem(n.label,n._value,n.attr);
                        /*if((k==0)&&labelCell){
                            kwLbl = objectUpdate(objectUpdate({},buildKw.lbl),kwLbl);
                            labelCell._('div',objectUpdate({'innerHTML':lbl,'text_align':'center'},kwLbl));
                        }*/
                        k++;
                    });
                }
            }
            if(cell.len()==0 && (that['slot_'+slot])){
                slotKw = objectExtract(kw,slot+'_*');
                slotValue = objectPop(kw,slot);
                lbl = objectPop(slotKw,'lbl');
                kwLbl = objectExtract(slotKw,'lbl_*');
                kwLbl = objectUpdate(objectUpdate({},buildKw.lbl),kwLbl);
                that['slot_'+slot](cell,slotValue,slotKw,kw.frameCode)
                if(labelCell){
                    labelCell._('div',objectUpdate({'innerHTML':lbl,'text_align':'center'},kwLbl));
                }
            }            
        });
        
        return table;
    },
    
    slot_searchOn:function(pane,slotValue,slotKw,frameCode){
        var div = pane._('div',{'width':slotKw.width || '15em'});
        div._('SearchBox', {searchOn:slotValue,nodeId:frameCode+'_searchbox',datapath:'.searchbox'});

    },
    slot_messageBox:function(pane,slotValue,slotKw,frameCode){        
        var mbKw = objectUpdate({duration:1000,delay:2000},slotKw);
        var subscriber = objectPop(mbKw,'subscribeTo');
        mbKw['subscribe_'+subscriber] = function(){
             var kwargs = arguments[0];
             var domNode = this.domNode;
             var sound = objectPop(kwargs,'sound');
             if(sound){
                 genro.playSound(sound);
             }
             var message = objectPop(kwargs,'message');
             var msgnode = document.createElement('span');
             msgnode.innerHTML = message;
             genro.dom.style(msgnode,kwargs);
             domNode.appendChild(msgnode);
             var customOnEnd = kwargs.onEnd;
             genro.dom.effect(domNode,'fadeout',{duration:objectPop(mbKw,'duration'),delay:objectPop(mbKw,'delay'),onEnd:function(){domNode.innerHTML=null;if(customOnEnd){customOnEnd();}}});
        }
        pane._('span',mbKw);
    }
});

//STORES

dojo.declare("gnr.widgets.SelectionStore", gnr.widgets.gnrwdg, {
     contentKwargs: function(sourceNode, attributes) {
         if ('name' in attributes){
             attributes['_name'] = objectPop(attributes,'name');
         }
         if ('content' in attributes){
             attributes['_content'] = objectPop(attributes,'content');
         }
         //attributes['path'] = attributes['storepath'];
         attributes.columns = attributes.columns || '==gnr.getGridColumns(this);';
         attributes.method = attributes.method || 'app.getSelection';
         if('chunkSize' in attributes && !('selectionName' in attributes)){
             attributes['selectionName'] = '*';
         }
         return attributes;
     },

     createContent:function(sourceNode, kw,children) {
         var chunkSize = objectPop(kw,'chunkSize',0);
         var storeType = chunkSize? 'VirtualSelection':'Selection';
         kw.row_count = chunkSize;
         var storeType = kw.row_count? 'VirtualSelection':'Selection';
         var identifier = objectPop(kw,'_identifier') || '_pkey';
         var selectionStore = sourceNode._('dataRpc',kw);
         var cb = "this.store.onLoaded(result,_isFiredNode);"
         selectionStore._('callBack',{content:cb});
         var rpcNode = selectionStore.getParentNode();
         rpcNode.store = new gnr.stores[storeType](rpcNode,{'identifier':identifier,'chunkSize':kw.row_count,'storeType':storeType});
         return selectionStore;
     }
});

dojo.declare("gnr.stores._Collection",null,{
    constructor:function(node,kw){
        this.storeNode = node;
        this.storepath = this.storeNode.attr.storepath;
        this.storeNode.setRelativeData(this.storepath,null);
        for (var k in kw){
            this[k] = kw[k];
        }
    },
    onLoaded:function(result){
        this.storeNode.setRelativeData(this.storepath,result);
        return result;
    },
    
    getData:function(){
        return this.storeNode.getRelativeData(this.storepath);
    },
    getItems:function(){
        return this.getData();
    },
    len:function(filtered){
        if(filtered && this._filtered){
            return this._filtered.length;
        }
        return this.getItems().length;
    },
    
    sort:function(sortedBy){
        this.sortedBy = sortedBy || this.sortedBy;
        var data = this.getData();
        data.sort(this.sortedBy);
    },
    
    absIndex:function(idx){
        if (this.filterToRebuild()) {
            console.log('invalid filter');
        }
        return this._filtered ? this._filtered[idx] : idx;
    },
  
    rowFromItem:function(item,grid){
        if(grid){
            return grid.rowFromBagNode(item);
        }
        return item;
    },
    getNavigationPkey:function(nav,currentPkey){
        var idx = nav == parseInt(nav) && nav;
        if(!idx){
            if(nav=='first'){
                idx = 0;
            }else if(nav=='last'){
                idx = this.len()-1;
            }else{
                idx = this.getIdxFromPkey(currentPkey);
                idx = nav=='next'? idx+1:idx-1;
            }
        }
        return this.getKeyFromIdx(idx);
    },
    
    getKeyFromIdx:function(idx){
        var data = this.getData();
        if(!data){
            return;
        }
        var item;
        data=data.getNodes()
        if ((idx<0)||( idx>(data.length-1))){
            return null;
        }    
        return this.keyGetter(data[idx]);
    },
    getIdxFromPkey:function(pkey){
        var result = -1;
        var data = this.getData();
        var that = this;
        if(pkey && data){
            data=data.getNodes();
            var k = -1;
            dojo.some(data,function(n){
                k++;
                if(that.keyGetter(n)==pkey){
                    result = k;
                    return true;
                }
            });
            return result;
        }
    },
    getGridRowDataByIdx:function(grid,idx){
        var rowdata={}
        var node=this.itemByIdx(idx);
        if (node){
            rowdata= grid.rowFromBagNode(node,this.externalChangedKeys);
        }
        return rowdata;
    },
    
    filterToRebuild: function(value) {
        this._filterToRebuild = value;
    },
    invalidFilter: function() {
        return this._filterToRebuild;
    },
    resetFilter: function() {
        return this._filtered = null;
    },
    
    compileFilter:function(value,filterColumn,colType){
        if(value==null){
            return null;
        }
        var cb;
        if (colType in {'A':null,'T':null}) {
            var regexp = new RegExp(value, 'i');
            cb = function(rowdata, index, array) {
                var columns = filterColumn.split('+');
                var txt = '';
                for (var i = 0; i < columns.length; i++) {
                    txt = txt + ' ' + rowdata[columns[i]];
                }
                return regexp.test(txt);
            };
        } else {
            var toSearch = /^(\s*)([\<\>\=\!\#]+)(\s*)(.+)$/.exec(value);
            if (toSearch) {
                var val;
                var op = toSearch[2];
                if (op == '=') {op = '==';}
                if ((op == '!') || (op == '#')) {op = '!=';}
                if (colType in {'R':null,'L':null,'I':null,'N':null}) {
                    val = dojo.number.parse(toSearch[4]);
                } else if (colType == 'D') {
                    val = dojo.date.locale.parse(toSearch[4], {formatLength: "short",selector:'date'});
                } else if (colType == 'DH') {
                    val = dojo.date.locale.parse(toSearch[4], {formatLength: "short"});
                }                
                cb = function(rowdata, index, array) {
                    return genro.compare(op,rowdata[filterColumn],val);
                };
            }
        }
        return cb;
    },

    createFiltered:function(grid,currentFilterValue,filterColumn,colType){
        var cb = this.compileFilter(currentFilterValue,filterColumn,colType);
        if (!cb && !grid.excludeListCb){
            this._filtered = null;
            return null;
        }
        var filtered=[]
        var excludeList = null;
        if (grid.excludeListCb) {
            excludeList = grid.excludeListCb();
        }
        dojo.forEach(this.getItems(), 
                    function(n,index,array){
                        var rowdata = grid.rowFromBagNode(n);
                        var result = cb? cb(rowdata,index,array):true; 
                        if(result){
                            if ((!excludeList)||(dojo.indexOf(excludeList, rowdata[grid.excludeCol]) == -1)) {
                                filtered.push(index);
                            }
                        }
                    });
        this._filtered=filtered;
        this._filterToRebuild=false;
    }
})

dojo.declare("gnr.stores.BagRows",gnr.stores._Collection,{
    keyGetter :function(n){
        return n.getValue('static').getItem(this.identifier);
    },
    getRowByIdx:function(idx){
        return 
    },
    getItems:function(){
        var data=this.getData();
        return data?data.getNodes():[];
    },
    rowFromItem:function(n,grid){
        if(grid){
            return grid.rowFromBagNode(n);
        }
        return n.getValue();
    }
});

dojo.declare("gnr.stores.Selection",gnr.stores.BagRows,{
    constructor:function(){
        var that = this;
        dojo.subscribe('dbevent_'+this.storeNode.attr.table.replace('.','_'),this,function(kw){
           that.onExternalChange(kw.changelist,kw.pkeycol);          
        });
    },
    onExternalChange:function(changelist,pkeycol){
        var eventdict = {};
        var dbevt,pkeys,wasInSelection,willBeInSelection;
        var insOrUpdKeys = [];
        var delKeys = [];
        var data = this.getData();
        var that = this;
        if(!data){
            return;
        }
        dojo.forEach(changelist,function(change){
            if (change['dbevent']=='D'){
                delKeys.push(change.pkey);
            }else{
                insOrUpdKeys.push(change.pkey);
            }
        });
        if (insOrUpdKeys.length>0) {
            genro.rpc.remoteCall('app.getSelection', 
                                objectUpdate({'_sourceNode':this.storeNode,
                                              'condition':' $'+pkeycol+' IN :_pkeys',_pkeys:insOrUpdKeys},
                                              this.storeNode.attr),
                                null,null,null,
                                function(result){
                                            willBeInSelection={};
                                            result.getValue().forEach(function(n){
                                                willBeInSelection[n.attr['_pkey']] = n.attr;
                                            },'static');
                                            that.checkExternalChange(delKeys,insOrUpdKeys,willBeInSelection);
                                            return result;
                                    });
        }else if (delKeys.length>0) {
            this.checkExternalChange(delKeys,[],[]);
        }

    },
    checkExternalChange:function(delKeys,insOrUpdKeys,willBeInSelection){
        var wasInSelection;
        var changed = false;
        var data = this.getData();
        var that = this;
        var pkeys,wasInSelection,wasInSelectionNode,willBeInSelectionNode,pkey;
        this.externalChangedKeys = this.externalChangedKeys || {};
        var wasInSelectionCb = function(pkeys){
            var result = {};
            data.forEach(function(n){
                if (dojo.indexOf(pkeys,n.attr._pkey)>=0){
                    result[n.attr._pkey] = n;
                }
            },'static');  
            return result;
        };
        if(delKeys.length>0){
            wasInSelection = wasInSelectionCb(delKeys);
             for(pkey in wasInSelection){
                 data.popNode(wasInSelection[pkey].label);
            }
        }
        if(insOrUpdKeys.length>0){
            wasInSelection = wasInSelectionCb(insOrUpdKeys);
            dojo.forEach(insOrUpdKeys,function(pkey){
                    wasInSelectionNode = wasInSelection[pkey];
                    willBeInSelectionNode = willBeInSelection[pkey];
                    if(wasInSelectionNode){
                        if (willBeInSelectionNode) {
                            that.externalChangedKeys[pkey] = true;
                            data.getNode(willBeInSelectionNode.label).updAttributes(willBeInSelectionNode.attr,true);
                            changed = true;
                        }else{
                            data.popNode(wasInSelectionNode.label);
                        }
                    }else if(willBeInSelectionNode){
                        that.externalChangedKeys[pkey] = true;
                        data.setItem('#id',willBeInSelectionNode);
                    }
                });
        }
        if(this.sortedBy){
            this.sort();
            this.storeNode.publish('updateRows');
        }
    },

    
    keyGetter :function(n){
        return n.attr[this.identifier];
    },
    
    rowFromItem:function(n,grid){
        if(grid){
            return grid.rowFromBagNode(n);
        }
        return n.attr();
    },
    itemByIdx:function(idx){
        var item=null;
        if (idx >= 0) {
            idx = this.absIndex(idx);
            var nodes=this.getItems()
            if (idx <= this.len()) {
                item=nodes[idx]
            }
        }
        return item
    }

});


dojo.declare("gnr.stores.VirtualSelection",gnr.stores.Selection,{
    constructor:function(){
        this.pendingPages = {};
        this.lastIdx =0;
    },
    len:function(){
        var data = this.getData();
        var len = data?data.getParentNode().attr['totalrows']:0;
        return len;
    },
    
    onLoaded:function(result,_isFiredNode){
        if(!_isFiredNode){
            this.externalChangedKeys = null;
        }
        this.clearBagCache();
        var selection = result.getValue(); 
        var data = new gnr.GnrBag();
        var resultattr = result.attr;
        data.setItem('P_0',result.getValue()); 
        this.rowtotal = resultattr.rowcount;
        this.totalRowCount = resultattr.totalRowCount;
        this.selectionName = resultattr.selectionName;
        this.storeNode.setRelativeData(this.storepath,data,resultattr);
        return result;
    },
    onExternalChangeResult:function(changelist,result){
        if(changelist.length>0){
            var that = this;
            this.externalChangedKeys = this.externalChangedKeys || {};
            dojo.forEach(changelist,function(n){
                that.externalChangedKeys[n.pkey] = true;
            });
            this.storeNode.fireNode();
        }
    },
    
    onExternalChange:function(changelist){
        var selectionKw = this.getData().getParentNode().attr;
        var that = this;
        var rpc_attr = objectUpdate({},this.storeNode.attr);
        objectUpdate(rpc_attr,{'selectionName':selectionKw.selectionName,
                                'changelist':changelist,'_sourceNode':this.storeNode});
        var result = genro.rpc.remoteCall('app.checkFreezedSelection', 
                                            rpc_attr,null,null,null,
                                         function(result){
                                             that.onExternalChangeResult(changelist,result)
                                             return result;
                                          });
    },

    
    clearBagCache:function() {
        var data = this.getData()
        if(data){
            data.clear();
        }
        this.currRenderedRowIndex = null;
        this.currRenderedRow = null;
        this.currCachedPageIdx = null;
        this.currCachedPage = null;
    },

    itemByIdx:function(idx,sync) {
        var delta = idx-this.lastIdx;
        this.lastIdx = idx;
        var dataPage;
        var rowIdx = idx % this.chunkSize;
        var pageIdx = (idx - rowIdx) / this.chunkSize;
        if (this.currCachedPageIdx != pageIdx) {
            if(!sync){
                dataPage=this.getDataChunk(pageIdx);
            }else{
                dataPage=this.getData().getItem('P_' + pageIdx);
                if (!dataPage){
                    dataPage = this.loadBagPageFromServer(pageIdx,sync);
                }
            }
            
            if (dataPage){
                this.currCachedPageIdx = pageIdx;
                this.currCachedPage=dataPage
                return this.currCachedPage.getNodes()[rowIdx]
            }else{
                this.currCachedPageIdx=-1;
                this.currCachedPage=null;
            }
        }else{
            if(((delta>0) && ((rowIdx/this.chunkSize)>.7 )) || ((delta<0) && ((rowIdx/this.chunkSize)<.3 ))){
                var guessPage = delta>0?pageIdx+1:pageIdx-1;
                if(guessPage>0){
                    if(guessPage!=this.guessPage){
                        this.getDataChunk(guessPage);
                        this.guessPage = guessPage;
                    }
                }
                
               
            }
            return this.currCachedPage.getNodes()[rowIdx]
        }
    },

    getDataChunk:function(pageIdx){

        if (pageIdx in this.pendingPages){
            return
        }else{
            var pageData=this.getData().getItem('P_' + pageIdx);
            if (pageData){
                return pageData;    
            }
            if(this.isScrolling){
                return
            }
            if(this.pendingTimeout){
                if (this.pendingTimeout.idx==pageIdx){
                    return
                }else{
                    clearTimeout(this.pendingTimeout.handler);
                    this.pendingTimeout = {};
                }
            }
            var that = this;
            this.pendingTimeout={'idx':pageIdx,
                                'handler':setTimeout(function(){
                                that.loadBagPageFromServer(pageIdx)
                                },10)
            };
            return
        }
    },
    onChunkLoaded:function(result,pageIdx){
        var data = result.getValue();
        this.getData().setItem('P_' + pageIdx, data,null,{'doTrigger':false});
        objectPop(this.pendingPages,pageIdx);
        this.storeNode.publish('updateRows');
        this.pendingTimeout = {};
       //if (this.pendingUpdateGrid){
       //    clearTimeout(this.pendingUpdateGrid);
       //}
       //var that = this;
       //this.pendingUpdateGrid=setTimeout(function(){
       //    that.storeNode.publish('updateRows');
       //},10);
        return data;
    },

    loadBagPageFromServer:function(pageIdx,sync) {
        var that = this;
        var row_start = pageIdx * this.chunkSize;
        var kw = this.getData().getParentNode().attr;
        var result = genro.rpc.remoteCall(kw.method, {'selectionName':kw.selectionName,
            'row_start':row_start,
            'row_count':this.chunkSize,
            'sortedBy':this.sortedBy,
            'table':kw.table,
            'recordResolver':false},
            null,
            null,
            null,
            sync?null:function(result){return that.onChunkLoaded(result,pageIdx)});
        if(sync){
            return this.onChunkLoaded(result,pageIdx);
        }else{
            this.pendingPages[pageIdx] = result;
        }
     },
     
     getIdxFromPkey:function(pkey){
        var result = -1;
        var dataNode = this.getData().getNodeByAttr('_pkey',pkey);
        if(dataNode){
            result = dataNode.attr.rowidx;
        }
        return result;
    },
    getKeyFromIdx:function(idx){
        var dataNode = this.itemByIdx(idx,true);
        //var dataNode = this.getData().getNodeByAttr('rowidx',idx);
        return this.keyGetter(dataNode);
    }
    
});




