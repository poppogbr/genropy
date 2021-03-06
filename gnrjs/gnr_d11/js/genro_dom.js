/*
 *-*- coding: UTF-8 -*-
 *--------------------------------------------------------------------------
 * package       : Genro js - see LICENSE for details
 * module genro_dom : Genro client utility functions
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

dojo.declare("gnr.GnrDomHandler", null, {

    constructor: function(application) {
        this.application = application;
        this.css3AttrNames = ['rounded','gradient','shadow','transform','transition'];
        this.styleAttrNames = ['height', 'width','top','left', 'right', 'bottom',
            'visibility','opacity', 'overflow', 'float', 'clear', 'display',
            'z_index', 'border','position','padding','margin',
            'color','white_space','vertical_align','background'].concat(this.css3AttrNames);
        
    },
    isStyleAttr:function(name) {
        for (var i = 0; i < this.styleAttrNames.length; i++) {
            if ((name == this.styleAttrNames[i]) || (name.indexOf(this.styleAttrNames[i] + '_') == 0)) {
                return true;
            }
        }
    },

    iFramePrint: function(iframe) {
        var contentWindow = genro.dom.iframeContentWindow(iframe);
        setTimeout(function() {
            contentWindow.print();
        }, 1);
    },

    iframeContentWindow: function(/* HTMLIFrameElement */iframe_el) {
        //	summary
        //	returns the window reference of the passed iframe
        var win = dijit.getDocumentWindow(genro.dom.iframeContentDocument(iframe_el)) ||
            // Moz. TODO: is this available when defaultView isn't?
                genro.dom.iframeContentDocument(iframe_el)['__parent__'] ||
                (iframe_el.name && document.frames[iframe_el.name]) || null;
        return win;	//	Window
    },

    iframeContentDocument: function(/* HTMLIFrameElement */iframe_el) {
        //	summary
        //	returns a reference to the document object inside iframe_el
        var doc = iframe_el.contentDocument // W3
                || (iframe_el.contentWindow && iframe_el.contentWindow.document) // IE
                || (iframe_el.name && document.frames[iframe_el.name] && document.frames[iframe_el.name].document)
                || null;
        return doc;	//	HTMLDocument
    },

    addStyleSheet:function(cssText, cssTitle) {
        var style = document.createElement("style");
        style.setAttribute("type", "text/css");
        style.setAttribute('title', cssTitle);
        if (style.styleSheet) {// IE
            var setFunc = function() {
                style.styleSheet.cssText = cssStr;
            };
            if (style.styleSheet.disabled) {
                setTimeout(setFunc, 10);
            } else {
                setFunc();
            }
        } else { // w3c
            var cssText = document.createTextNode(cssText);
            style.appendChild(cssText);
        }
        document.getElementsByTagName("head")[0].appendChild(style);
        style.disabled = false; //to control why appending child style change disable attr
    },
    loadCss: function(url, cssTitle) {
        var e = document.createElement("link");
        e.href = url;
        e.type = "text/css";
        e.rel = "stylesheet";
        e.media = "screen";
        document.getElementsByTagName("head")[0].appendChild(e);
    },
    loadJs: function(url) {
        var e = document.createElement("script");
        e.src = url;
        e.type = "text/javascript";
        document.getElementsByTagName("head")[0].appendChild(e);
    },

    addClass: function(where, cls) {
        if (typeof(cls) == 'string') {
            var domnode = this.getDomNode(where);
            if (!domnode) return;
            var classes = cls.split(' ');
            for (var i = 0; i < classes.length; i++) {
                if (domnode.addClass) {
                    domnode.addClass(classes[i]);
                } else {
                    dojo.addClass(domnode, classes[i]);
                }

            }
        }
    },
    themeAttribute:function(topic,property,dflt){
        var topic = genro.theme[topic];
        return topic? topic[property]:dflt;
    },
    
    style:function(where, attr, value) {
        var domnode = this.getDomNode(where);
        if (domnode) {
            if (typeof (attr) == 'string') {
                dojo.style(domnode, genro.dom.dojoStyleAttrName(attr), value);
            } else {
                var kw = {};
                for (k in attr) {
                    kw[genro.dom.dojoStyleAttrName(k)] = attr[k];
                }
                dojo.style(domnode, kw);
            }

        }
    },
    dojoStyleAttrName:function(attr) {
        if (attr.indexOf('_')) {
            attr = attr.split('_');
        } else if (attr.indexOf('-')) {
            attr = attr.split('-');
        } else {
            return attr;
        }
        var r = attr.splice(0, 1);
        dojo.forEach(attr, function(n) {
            r = r + stringCapitalize(n);
        });
        return r;
    },
    getDomNode: function(where) {
        if (typeof (where) == 'string') {
            var where = genro.domById(where);
        }
        if (!where) {
            return;
        }
        if (where instanceof gnr.GnrDomSourceNode) {
            where = where.getDomNode();
        } else if (where instanceof gnr.GnrDomSource) {
            where = where.getParentNode().getDomNode();
        }
        return where;
    },
    removeClass: function(where, cls) {
        if (typeof(cls) == 'string') {
            var domnode = this.getDomNode(where);
            if (!domnode) return;
            var classes = cls.split(' ');
            for (var i = 0; i < classes.length; i++) {
                if (domnode.removeClass) {
                    domnode.removeClass(classes[i]);
                } else {
                    dojo.removeClass(domnode, classes[i]);
                }
            }
        }

    },
    setClass:function(where, cls, set) {
        if (set == 'toggle') {
            genro.dom.toggleClass(where, cls);
        }
        else if (set) {
            this.addClass(where, cls);
        } else {
            this.removeClass(where, cls);
        }
    },
    toggleClass:function(where, cls) {
        if (typeof(cls) == 'string') {
            var toggle = function (n, c) {
                dojo[dojo.hasClass(n, c) ? 'removeClass' : 'addClass'](n, c);
            };
            var domnode = this.getDomNode(where);
            if (!domnode) return;
            var classes = cls.split(' ');
            for (var i = 0; i < classes.length; i++) {
                if (domnode.forEach) {
                    domnode.forEach(function(n) {
                        toggle(n, classes[i]);
                    });
                } else {
                    toggle(domnode, classes[i]);
                }
            }
        }
    },
    bodyClass:function(cls, set) {
        genro.dom.setClass(dojo.body(), cls, set);
    },

    disable:function(where) {
        this.addClass(where, 'disabled');
    },
    enable:function(where) {
        this.removeClass(where, 'disabled');
    },
    hide:function(where) {
        this.addClass(where, 'hidden');
    },
    show:function(where) {
        this.removeClass(where, 'hidden');
    },
    toggleVisible:function(where, visible) {
        if (visible) {
            this.show(where);
        } else {
            this.hide(where);
        }
    },
    effect:function(where, effect, kw) {
        var anim;
        var effect = effect.toLowerCase();
        var kw = kw || {};
        if (typeof (where) == 'string') {
            var where = genro.domById(where);
        }
        if (!where) {
            return;
        }
        kw.node = where;
        kw.duration = kw.duration || 300;
        if (effect == 'fadein') {
            genro.dom.style(where, {opacity:0});
            anim = dojo.fadeIn(kw);
        }
        else if (effect == 'fadeout') {
            genro.dom.style(where, {opacity:1});
            anim = dojo.fadeOut(kw);
        }
        else if (effect == 'wipein') {
            anim = dojo.fx.wipeIn(kw);
        }
        else if (effect == 'wipeout') {
            anim = dojo.fx.wipeOut(kw);
        }
        else {
            //genro.debug('the effect does not exist','console') ;
            return;
        }
        anim.play();
        return anim;
    },
    ghostOnEvent:function(evt) {
        evt_type = evt.type;
        if (evt_type == 'focus' || evt_type == 'blur') {
            genro.dom[evt_type == 'focus' ? 'addClass' : 'removeClass'](evt.target.id + "_label", "ghostpartial");
        }
        else if (evt_type == 'keyup' || evt_type == 'keypress') {
            genro.dom[evt.target.value.length > 0 ? 'addClass' : 'removeClass'](evt.target.id + "_label", "ghosthidden");
        } else if (evt_type == 'setvalue') {
            genro.dom[evt.value.length > 0 ? 'addClass' : 'removeClass'](evt.obj.id + "_label", "ghosthidden");
        }
    },
    html_maker:function(kw, bagnode) {
        kw = genro.evaluate(kw);
        return genro.dom['html_' + kw.widget](kw, bagnode);
    },
    html_checkbox:function(kw, bagnode) {
        if ('value' in kw) {
            var path = kw.value;
            kw.onclick = dojo.hitch(bagnode, function(e) {
                var v = e.target.checked;
                this.setAttr(path, v);
            });
            kw.checked = bagnode.getAttr(path);
        }
        return '<input type="checkbox" name="' + kw.name + '" checked="' + kw.checked + '" id="' + kw.id + '" onclick="' + kw.onclick + '"><label for="' + kw.id + '">' + kw.label + '</label>';
    },

    html_select:function(kw) {
        var values = kw.values.split(',');
        var wdg = '<label for="' + kw.id + '">' + kw.label + '</label>';
        wdg = wdg + '<select name="' + kw.name + '" id="' + kw.id + '" onchange="' + kw.onchange + '" size="1">';
        wdg = wdg + '<option value="false">&nbsp</option>';
        for (var i = 0; i < values.length; i++) {
            var val = values[i];
            var subwdg = null;
            if (val.indexOf(':')) {
                val = val.split(':');
                subwdg = '<option value="' + val[0] + '">' + val[1] + '</option>';
            } else {
                subwdg = '<option value="' + val + '">' + val + '</option>';
            }
            wdg = wdg + subwdg;
        }
        ;
        wdg = wdg + '</select>';
        return wdg;
    },

    enableDisableNodes:function(where) {
        if (typeof (where) == 'string') {
            var where = genro.domById(where);
        }
    },
    resizeContainer:function(wdgt) {
        if (wdgt.parent && wdgt.parent.isContainer) {
            this.resizeContainer(wdgt.parent);
        } else if (wdgt.isContainer) {
            wdgt.onResized();
        }
    },

    getStyleDict: function(attributes/*{}*/, noConvertStyle) {
        if (attributes.gnrIcon) {
            attributes.iconClass = 'gnrIcon gnrIcon' + objectPop(attributes, 'gnrIcon');
        }
        var noConvertStyle = noConvertStyle || [];
        var styledict = objectFromStyle(objectPop(attributes, 'style'));
        var attrname;
        dojo.forEach(this.css3AttrNames,function(name){
            var value=objectPop(attributes,name);
            var valuedict=objectExtract(attributes,name+'_*');
            if(value || objectNotEmpty(valuedict)){
                genro.dom['css3style_'+name](value,valuedict,styledict,noConvertStyle);
            }
        });
        for (var i = 0; i < this.styleAttrNames.length; i++) {
            attrname = this.styleAttrNames[i];
            if (attrname in attributes && arrayIndexOf(noConvertStyle, attrname) == -1) {
                styledict[attrname.replace('_', '-')] = objectPop(attributes, attrname);
            }
        }
        this.style_setall('min', styledict, attributes, noConvertStyle);
        this.style_setall('max', styledict, attributes, noConvertStyle);
        this.style_setall('background', styledict, attributes, noConvertStyle);
        this.style_setall('text', styledict, attributes, noConvertStyle);
        this.style_setall('font', styledict, attributes, noConvertStyle);
        this.style_setall('margin', styledict, attributes, noConvertStyle);
        this.style_setall('padding', styledict, attributes, noConvertStyle);
        this.style_setall('border', styledict, attributes, noConvertStyle);
        this.style_setall('overflow', styledict, attributes, noConvertStyle);
        return styledict;
    },
    css3style_transform:function(value,valuedict, styledict,noConvertStyle){
        var key= dojo.isSafari?'-webkit-transform':'-moz-transform';
        var result='';
        if('rotate' in valuedict){result+='rotate('+(valuedict['rotate']||'0')+'deg ) ';}
        if('translate' in valuedict){result+='translate('+valuedict['translate']+') ';}
        if('translate_x' in valuedict){result+='translatex('+(valuedict['translate_x']||'0')+'px) ';}
        if('translate_y' in valuedict){result+='translatey('+(valuedict['translate_y']||'0')+'px) ';}
        if('scale' in valuedict){result+='scale('+(valuedict['scale']||0)+') ';}
        if('scale_x' in valuedict){result+='scalex('+(valuedict['scale_x']||1)+') ';}
        if('scale_y' in valuedict){result+='scaley('+(valuedict['scale_y']||1)+') ';}
        if('skew' in valuedict){result+='skew('+valuedict['skew']+') ';}
        if('skew_x' in valuedict){result+='skewx('+(valuedict['skew_x']||0)+'deg) ';}
        if('skew_y' in valuedict){result+='skewy('+(valuedict['skew_y']||0)+'deg) ';}
        styledict[key] = result;
    },
     css3style_transition:function(value,valuedict, styledict,noConvertStyle){
        var key= dojo.isSafari?'-webkit-transition':'-moz-transition';
         
        transition_property='width,height'
        if(value){
            styledict[key] = value;
        }
        for (var prop in valuedict){
            value=valuedict[prop]
            if (prop=='function'){prop='timing-function'}
            if (((prop=='duration') ||(prop=='delay')) && ((value+'').indexOf('s')<0)){value=value+'s'}
            styledict[key+'-'+prop] = value;
        }
        
        
    },
    css3style_shadow:function(value,valuedict, styledict,noConvertStyle){
        var inset = false;
        var value = value || '0px 0px 0px gray';
        if(value.indexOf('inset')>=0){
            inset = true;
            value = value.replace('inset','');
        }
        var shadow = splitStrip(value,' ');
        var x = ((valuedict['x'] || shadow[0])+'').replace('px','');
        var y = ((valuedict['y'] || shadow[1])+'').replace('px','');
        var blur = ((valuedict['blur'] || shadow[2])+'').replace('px','');
        var color = valuedict['color'] || shadow[3];
        var inset = 'inset' in valuedict? valuedict['inset'] : inset;
        var result = x+'px '+y+'px '+blur+'px '+color;
        if(inset){
            result+= ' inset';
        }
        var key = dojo.isSafari? '-webkit-box-shadow':'-moz-box-shadow';
        styledict[key] = result;
    },
    css3style_gradient:function(value,valuedict,styledict, noConvertStyle){
        if(value){
            styledict['background-image'] = value;
        }
        if(objectNotEmpty(valuedict)){
            var colordict=objectExtract(valuedict,'color_*');
            colors=[];
            for(var col in colordict){colors.push(col);}
            colors.sort();
            var color_from=valuedict['from'];
            var color_to=valuedict['to'];
            if(dojo.isSafari){
                var d=parseInt(valuedict['deg'] || 0);
                d=(d+360)%360;
                if((d>=0) && (d<45)){x1=0;x2=100;y1=50+(d/45)*50;y2=100-y1;}
                else if((d>=45) && (d<135)){y2=0;y1=100;x2=((135-d)/90)*100;x1=100-x2;}
                else if((d>=135) && (d<225)){x1=100;x2=0;y1=((225-d)/90)*100;y2=100-y1;}
                else if((d>=225) && (d<315)){y2=100;y1=0;x1=((315-d)/90)*100;x2=100-x1;}
                else if((d>=315) &&( d<360)){x1=0;x2=100;y1=50-(((360-d)/45)*50);y2=100-y1;}
                var r= [Math.round(x1,2),Math.round(y1,2),Math.round(x2,2),Math.round(y2,2)];
                var result = "-webkit-gradient(linear, ";
                result += r[0]+"% "+r[1]+"%,"+ r[2]+"% "+r[3]+"% ";
                if (colors.length>0){
                    dojo.forEach(colors,function(col){
                        var c=(colordict[col]+',0').split(',');
                        result +=", color-stop("+c[1]+"%, "+c[0]+")";
                    });
                }else{
                    result+=", from("+valuedict['from']+"), to("+valuedict['to']+")";
                }
               
            }else{
                var result = '-moz-'+(valuedict['type'] || 'linear');
                result += '-gradient(';
                result += (valuedict['deg'] || 0)+'deg ';
                if (colors.length>0){
                       dojo.forEach(colors,function(col){
                        var c=(colordict[col]+',0').split(',');
                        result +=", "+c[0]+" "+c[01]+"%";
                    });
                }else{
                    result += ','+color_from+','+color_to;
                }
                
            }
            styledict['background-image']= result+')';
        }
        
    },
    
    css3style_rounded:function(value,valuedict,styledict, noConvertStyle){
        var v;
        var cb=dojo.isSafari? function(y,x){return '-webkit-border-'+y+'-'+x+'-radius';}: 
                                function(y,x){
                                    return '-moz-border-radius-'+y+x;};
        var rounded_corners = this.normalizedRoundedCorners(value,valuedict);
        for(var k in rounded_corners){
            var v = rounded_corners[k]
            k=k.split('_')
            styledict[cb(k[0],k[1])] = v+'px';
        }

    },
    
    normalizedRoundedCorners : function(rounded,rounded_dict){
        var result = {};
        var v,m;
        if(rounded){
            rounded_dict['all'] = rounded;
        }
        var converter = [['all','tr','tl','br','bl'],
                         ['top','tr','tl'],
                         ['bottom','br','bl'],
                         ['right','tr','br'],
                         ['left','tl','bl'],
                         ['top_left','tl'],['left_top','tl'],
                         ['top_right','tr'],['right_top','tr'],
                         ['bottom_left','bl'],['left_bottom','bl'],
                         ['bottom_right','br'],['right_bottom','br']];
        if(objectNotEmpty(rounded_dict)){
            dojo.forEach(converter,function(k){
                if(k[0] in rounded_dict){
                    v = rounded_dict[k[0]];
                    for(var i=1; i<k.length; i++){
                        m = k[i];
                        result[(m[0]=='t'? 'top':'bottom')+'_'+(m[1]=='l'? 'left':'right')]=v
                    }
                }
            });
        }
        return result
    },
    
    style_setall:  function(label, styledict/*{}*/, attributes/*{}*/, noConvertStyle) {
        for (var attrname in attributes) {
            if (stringStartsWith(attrname, label + '_') && arrayIndexOf(noConvertStyle, attrname) == -1) {
                styledict[attrname.replace('_', '-')] = objectPop(attributes, attrname);
            }
        }
    },
    addCssRule: function(rule) {
        var styles = document.styleSheets;
        for (var i = 0; i < styles.length; i++) {
            var stylesheet = styles[i];
            if (stylesheet.title == 'localcss') {
                if (stylesheet.insertRule) {
                    stylesheet.insertRule(rule, 0);
                }
                else {
                    splittedrule = /(.*)\{(.*)\}/.exec(rule);
                    if (splittedrule[1] && splittedrule[2]) stylesheet.addRule(splittedrule[1], splittedrule[2]);
                }
                break;
            }
        }

    },
    cssRulesToBag:function(rules) {
        var result = new gnr.GnrBag();
        var _importRule = 3;
        var _styleRule = 1;
        var rule,label,value,attr;
        for (var i = 0, len = rules.length; i < len; i++) {
            r = rules.item(i);
            switch (r.type) {
                case _styleRule:
                    label = 'r_' + i;
                    value = genro.dom.styleToBag(r.style);
                    result.setItem(label, value, {selectorText:r.selectorText,_style:r.style});
                    this.css_selectors[r.selectorText] = value;
                    break;
                case _importRule:
                    attr = {href:r.href};
                    label = r.title || 'r_' + i;
                    result.setItem(label, genro.dom.cssRulesToBag(r.styleSheet.cssRules), attr);

                    break;
                // default:
                //     console.log('cssRulesToBag(): rule #' + i);
                //     console.log(r);
            }
        }
        ;

        return result;
    },
    setSelectorStyle: function(selector, kw, path) {
        var path = path || 'gnr.stylesheet';
        var selectorbag = this.css_selectors[selector];
        for (st in kw) {
            selectorbag.setItem(st, kw[st]);
        }
    },
    getSelectorBag: function(selector) {
        return this.css_selectors[selector];
    },
    styleSheetBagSetter:function(value, kw) {
        var setters = objectExtract(kw, '_set_*', true);
        for (var setter in setters) {
            var setlist = setters[setter].split(':');
            var s = {};
            s[setter.replace('_', '-')] = genro.evaluate(setlist.slice(1).join(':').replace('#', value));
            genro.dom.setSelectorStyle(setlist[0], s);
        }
    },

    styleSheetsToBag:function() {
        var styleSheets = document.styleSheets;
        var result = new gnr.GnrBag();
        var label,value,attr;
        var cnt = 0;
        this.css_selectors = {};
        dojo.forEach(styleSheets, function(s) {
            label = s.title || 's_' + cnt;
            attr = {'type':s.type,'title':s.title};
            value = genro.dom.cssRulesToBag(s.cssRules);
            result.setItem(label, value, attr);
            cnt++;
        });
        return result;
    },
    styleToBag:function(s) {
        result = new gnr.GnrBag();
        var rule;
        // for (var i=0; i < s.length; i++) {
        //     st = s[i];
        //     result.setItem(st, s.getPropertyValue(st)); 
        // };
        for (var i = s.length; s--;) {
            var st = s[i];
            result.setItem(st, s.getPropertyValue(st));
        }
        return result;
    },
    windowTitle:function(title) {
        document.title = title;
    },
    styleTrigger:function(kw) {
        var parentNode = kw.node.getParentNode();
        var st = parentNode.attr._style;
        if (!st) {
            return;
        }
        if (kw.evt == 'upd') {
            st.setProperty(kw.node.label, kw.value, null);
        } else if (kw.evt == 'ins') {
            st.setProperty(kw.node.label, kw.node.getValue(), null);
        } else if (kw.evt == 'del') {
            // console.log(kw);
        }
        var stylebag = genro.dom.styleToBag(st);
        parentNode.setValue(stylebag);
        this.css_selectors[parentNode.attr.selectorText] = stylebag;
    },
    cursorWait:function(flag) {
        if (flag) {
            genro.dom.addClass(document.body, 'cursorWait');
        } else {
            genro.dom.removeClass(document.body, 'cursorWait');
        }
    },
    makeReadOnlyById:function(fieldId) {
        var field = dojo.byId(fieldId);
        field.readOnly = true;
        field.style.cursor = 'default';
        dojo.connect(field, 'onfocus', function () {
            field.blur();
        });
    },
    showHideSubRows:function (evt) {
        var row = evt.target.parentNode.parentNode;
        var currlevel = row.getAttribute('lvl');
        var newstatus = '';
        if (row.getAttribute('isclosed') != 'y') {
            newstatus = 'y';
        }
        row.setAttribute('isclosed', newstatus);

        var rows = row.parentNode.rows;
        var rowlevel, sublevel;
        for (var i = 0; i < rows.length; i++) {
            rowlevel = rows[i].getAttribute('lvl');
            if (rowlevel.indexOf(currlevel) == 0) {  //row level starts with currlevel
                if (rowlevel != currlevel) {      //but is longer (is a sublevel)
                    if (newstatus == 'y') { // hide all subchild
                        rows[i].setAttribute('rowhidden', newstatus);
                        if (rowlevel.slice(-2) != '._') {
                            rows[i].setAttribute('isclosed', newstatus);
                        }
                    } else {
                        sublevel = rowlevel.replace(currlevel + '.', '');
                        if (sublevel.indexOf('.') < 0) { // open only first level subchild
                            rows[i].setAttribute('rowhidden', newstatus);
                        }
                    }
                }
            }
        }
    },
    parseXmlString:function (txt) {
        var result;
        if (dojo.isIE) {
            result = new ActiveXObject("Microsoft.XMLDOM");
            result.async = "false";
            result.loadXML(txt);
        } else {
            var parser = new DOMParser();
            result = parser.parseFromString(txt, 'text/xml');	//	DOMDocument
        }
        return result;
    },
    dispatchKey: function(keycode, domnode) {
        var domnode = domnode || document.body;
        var e = document.createEvent('KeyboardEvent');
        // Init key event
        e.initKeyEvent('keydown', true, true, window, false, false, false, false, keycode, 0);
        // Dispatch event into document
        domnode.dispatchEvent(e);
    },
    canBeDropped:function(dataTransfer, sourceNode) {
        var dragSourceInfo = genro.dom.getDragSourceInfo(dataTransfer);
        if (dragSourceInfo.detachable) {
            return 'detach';
        }
        var inherited = sourceNode.getInheritedAttributes();
        var supportedTypes = sourceNode.getInheritedAttributes().dropTypes;
        var supportedTypes = supportedTypes ? splitStrip(supportedTypes) : [];
        for (var k in objectExtract(inherited, 'onDrop_*', true)) {
            supportedTypes.push(k);
        }
        var draggedTypes = genro.dom.dataTransferTypes(dataTransfer);
        var matchCb=function(supportedType) {
                return arrayMatch(draggedTypes, supportedType).length > 0;
        };
        if (dojo.filter(supportedTypes, matchCb).length == 0) {
                return false;
        }
        var dropTags = sourceNode.getInheritedAttributes().dropTags;
        if (!dropTags) {
            return true;
        }
        //var dragTags=dataTransfer.getData('dragTags') || '';
        var dragTags = dragSourceInfo.dragTags;
        if (!dragTags) {
            return false;
        }
        var dragTags = splitStrip(dragTags, ',');
        var or_conditions = splitStrip(dropTags, ',');
        valid = false;
        for (var i = 0; ((i < or_conditions.length) && !valid); i++) {
            var valid = true;
            var or_condition = or_conditions[i].replace(/' NOT '/g, ' AND !');
            or_condition = splitStrip(or_condition, ' AND ');
            for (var j = 0; ((j < or_condition.length) && valid); j++) {
                var c = or_condition[j];
                exclude = false;
                if (c[0] == '!') {
                    c = c.slice(1);
                    exclude = true;
                }
                var match = dojo.some(dragTags, function(k) {
                    return k == c;
                });
                valid = exclude ? !match : match;
            }
            ;

        }
        ;
        return valid;

    },
    onDragOver:function(event) {
        if (genro._lastDropTarget != event.target) {
            if (genro._lastDropTarget) {
                genro.dom.onDragLeave(event);
            }
            genro._lastDropTarget = event.target;
            genro.dom.onDragEnter(event);
        }
        event.stopPropagation();
        event.preventDefault();
        event.dataTransfer.dropEffect = "move";

    },
    getDragDropInfo:function(event) {
        var domnode = event.target;
        while (!domnode.getAttribute) {
            domnode = domnode.parentNode;
        }
        var info = {'domnode':domnode};
        info.modifiers = genro.dom.getEventModifiers(event);
        var widget,handler,sourceNode;
        if (domnode.sourceNode) {
            info.handler = domnode.gnr;
            info.sourceNode = domnode.sourceNode;
            info.nodeId = domnode.sourceNode.attr.nodeId;
        }
        else {
            widget = dijit.getEnclosingWidget(domnode);
            if(!widget){
                return;
            }
            var rootwidget = widget.sourceNode ? widget : widget.grid || widget.tree;
            info.widget = widget;
            if (!rootwidget) {
                return;
            }
            info.handler = rootwidget.gnr;
            info.sourceNode = rootwidget.sourceNode;
            info.nodeId = info.sourceNode.attr.nodeId;
        }
        info.event = event;
        if (event.type == 'dragstart') {
            info.dragmode = domnode.getAttribute('dragmode');
            info.handler.fillDragInfo(info);
            info.drag = true;
        } else {
            info.drop = true;
            var sourceNode = info.sourceNode;
            var attr = sourceNode.attr;
            var dropTarget = sourceNode.dropTarget || attr.selfDragRows || attr.selfDragColumns;
            var dropTargetCb = sourceNode.dropTargetCb;
            info.dragSourceInfo = genro.dom.getDragSourceInfo(event.dataTransfer);
            if (info.dragSourceInfo.detachable) {
                return info;
            }
            if (dropTarget || dropTargetCb) {
                info.sourceNodeId = info.dragSourceInfo.nodeId;
                info.selfdrop = (info.nodeId && (info.nodeId == info.sourceNodeId));
                info.hasDragType = function() {
                    var draggedTypes = genro.dom.dataTransferTypes(event.dataTransfer);
                    return (dojo.filter(arguments,
                                       function (value) {
                                           return dojo.indexOf(draggedTypes, value) >= 0;
                                       }).length > 0);
                };
                var continueDrop = ! (info.handler.fillDropInfo(info) === false);
                if (!continueDrop || ( dropTargetCb && (! dropTargetCb(info)))) {
                    info = null;
                }
            }
            else {
                info = null;
            }
        }
        return info;
    },
    onDragLeave:function(event) {
        if (genro.dom._dragLastOutlined) {
            genro.dom.removeClass(genro.dom._dragLastOutlined, 'canBeDropped');
            genro.dom.removeClass(genro.dom._dragLastOutlined, 'cannotBeDropped');
            genro.dom._dragLastOutlined = null;
        }
    },
    onDragEnter:function(event) {
        var dropInfo = this.getDragDropInfo(event);

        if (!dropInfo) {
            //console.log('not drag_info')
            return;
        }
        event.stopPropagation();
        event.preventDefault();
        var sourceNode = dropInfo.sourceNode;
        var dataTransfer = event.dataTransfer;
        var canBeDropped = this.canBeDropped(dataTransfer, sourceNode);
        dataTransfer.effectAllowed = canBeDropped ? 'move' : 'none';
        dataTransfer.dropEffect = canBeDropped ? 'move' : 'none';
        if (canBeDropped != 'detach') {
            genro.dom.outlineShape(dropInfo.outline, canBeDropped, event);
        }
    },
    outlineShape:function(shape, canBeDropped) {
        if (genro.dom._dragLastOutlined) {
            genro.dom.removeClass(genro.dom._dragLastOutlined, 'canBeDropped');
            genro.dom.removeClass(genro.dom._dragLastOutlined, 'cannotBeDropped');
            genro.dom._dragLastOutlined = null;
        }
        if (shape) {
            genro.dom.setClass(shape, 'cannotBeDropped', !canBeDropped);
            genro.dom.setClass(shape, 'canBeDropped', canBeDropped);
            genro.dom._dragLastOutlined = shape;
        } else {
            genro.dom.removeClass(dojo.body(), 'drag_started');
            genro.dom.removeClass(dojo.body(), 'drag_to_trash');
        }
    },
    onDetach:function(sourceNode, dropInfo) {
        var domnode = sourceNode.getDomNode();
        var coords = dojo.coords(domnode);
        var title = sourceNode.getInheritedAttributes().title || 'Untitled';
        var detached_id = 'detached_' + sourceNode._id;
        if (sourceNode.isPointerPath(title)) {
            var pointer = title[0];
            title = sourceNode.absDatapath(title);
            title = pointer + title;
        }

        var floating = genro.dlg.floating({'nodeId':'floating_' + sourceNode._id,
            'title':title ,'top':dropInfo.event.pageY + 'px',
            'left':dropInfo.event.pageX + 'px',resizable:true,
            dockable:true,closable:false,dockTo:detached_id});

        floating._('div', {height:coords.h + 'px',width:coords.w + 'px',_class:'detatched_placeholder',id:detached_id});
        floating = floating.getParentNode().widget;
        var placeholder = floating.containerNode.firstElementChild;
        var currentParent = domnode.parentNode;
        currentParent.replaceChild(placeholder, domnode);
        floating.containerNode.appendChild(domnode);
        sourceNode.attr.isDetached = true;
        dojo.connect(floating, 'hide', function() {
            var widget = dijit.getEnclosingWidget(placeholder);
            widget.setContent(domnode);
            sourceNode.attr.isDetached = false;
            //currentParent.replaceChild(domnode,placeholder);
            floating.close();
        });
        floating.show();
        coords.h = coords.h + dojo.coords(floating.domNode).h;
        floating.resize(coords);
    },
    onDrop:function(event) {
        genro.dom.outlineShape(null);
        event.stopPropagation();
        var dropInfo = this.getDragDropInfo(event);
        if (!dropInfo) {
            event.preventDefault();
            return;
        }
        var domnode = dropInfo.domnode;
        var sourceNode = dropInfo.sourceNode;
        var dataTransfer = event.dataTransfer;
        var dragSourceInfo = genro.dom.getDragSourceInfo(dataTransfer);
        if (dragSourceInfo.detachable) {
            event.preventDefault();
            genro.dom.onDetach(genro.src.nodeBySourceNodeId(dragSourceInfo._id), dropInfo);
            return;
        }
        var canBeDropped = this.canBeDropped(dataTransfer, sourceNode); // dovrei già essere bono
        if (canBeDropped) {
            var inherited = sourceNode.getInheritedAttributes();
            event.preventDefault();
            var dropped = null;
            var dataTransferTypes = genro.dom.dataTransferTypes(dataTransfer);
            var dropTypes = (inherited.dropTypes || 'text/plain').split(',');
            var params = {'dropInfo':dropInfo};
            if ((dojo.indexOf(dataTransferTypes, 'Files') >= 0 ) && (dojo.indexOf(dropTypes, 'Files') >= 0)) {
                genro.dom.onDrop_files(dataTransfer, inherited, params, sourceNode);
            } else {
                genro.dom.onDrop_standard(dataTransfer, inherited, params, sourceNode, dropTypes, dataTransferTypes);
            }
        }
    },
    onDrop_files:function(dataTransfer, inherited, params, sourceNode) {
        var onDropAction = inherited.onDrop;
        if (!onDropAction) {
            return;
        }
        var drop_ext = inherited.drop_ext;
        var valid_ext = drop_ext ? splitStrip(drop_ext) : null;
        var files = [];
        dojo.forEach(dataTransfer.files, function(f) {
            if ((!valid_ext) || (dojo.indexOf(valid_ext, f['name'].split('.').pop()) >= 0)) {
                files.push(f);
            }
        });
        if (files.length > 0) {
            params['files'] = files;
            funcApply(onDropAction, params, sourceNode);
        }
    },
    onDrop_standard:function(dataTransfer, inherited, params, sourceNode, dropTypes, dataTransferTypes) {
        var onDropAction = inherited.onDrop;
        var values = {};
        for (var i = 0; i < dataTransferTypes.length; i++) {
            var datatype = dataTransferTypes[i];
            if (datatype.indexOf('sourceNode_') == 0) {
                continue;
            }
            var datatype_code = datatype.replace(/\W/g, '_');
            var inDropTypes = (dojo.filter(dropTypes,
                                          function(dropType) {
                                              return datatype.match(dropType.replace('*', '(.*)'));
                                          }).length > 0);
            //var inDropTypes = dataTransferTypes[i].match()//(arrayMatch(dropTypes,dataTransferTypes[i]).length>0);
            if (inherited['onDrop_' + datatype_code] || inDropTypes) {
                var value = genro.dom.getFromDataTransfer(dataTransfer, datatype);
                if (inherited['onDrop_' + datatype_code]) {
                    params['data'] = value;
                    funcApply(inherited['onDrop_' + datatype_code], params, sourceNode);
                } else if (inDropTypes) {
                    values[datatype_code] = value;
                }
            }
        }
        if (objectNotEmpty(values) && onDropAction) {
            params['data'] = values;
            funcApply(onDropAction, params, sourceNode);
        }
    },
    onDragStart:function(event) {
        event.stopPropagation();
        if (event.target.draggable === false) {
            event.preventDefault();
            return false;
        }
        var dragInfo = this.getDragDropInfo(event);
        var sourceNode = dragInfo.sourceNode;

        if (dragInfo.sourceNode.getAttributeFromDatasource('detachable')) {
            if (!event.shiftKey || sourceNode.attr.isDetached) {
                event.preventDefault();
                return;
            }
        }
        var dragValues = dragInfo.handler.onDragStart(dragInfo);
        if (dragValues === false) {
            return false;
        }
        var inherited = sourceNode.getInheritedAttributes();
        if ('onDrag' in inherited) {
            var doDrag = funcCreate(inherited['onDrag'], 'dragValues,dragInfo,treeItem')(dragValues, dragInfo, dragInfo.treeItem);
            if (doDrag === false) {
                return;
            }
        }
        var domnode = dragInfo.target;
        var widget = dragInfo.widget;
        genro.dom._transferObj = {};
        var dataTransfer = event.dataTransfer;
        if (!dragInfo.dragImageNode) {
            var dragClass = inherited['dragClass'] || 'draggedItem';
            if (dragClass) {
                genro.dom.addClass(dragInfo.domnode, dragClass);
                dragInfo.dragClass = dragClass;
                setTimeout(function() {
                    genro.dom.removeClass(dragInfo.domnode, dragClass);
                }, 1);
            }
        }

        if ('trashable' in dragValues) {
            if (widget) {
                if (widget.gnr.setTrashPosition(dragInfo)) {
                    genro.dom.addClass(dojo.body(), 'drag_to_trash');
                }
                ;
            }
        }
        var dragTags = inherited['dragTags'];
        var local_dragTags = objectPop(dragValues, 'dragTags');
        dragTags = dragTags ? (local_dragTags ? dragTags + ',' + local_dragTags : dragTags ) : local_dragTags;
        genro.dom.setDragSourceInfo(dragInfo, dragValues, dragTags);
        for (var k in dragValues) {
            genro.dom.setInDataTransfer(dataTransfer, k, dragValues[k]);
        }
        genro.dom._lastDragInfo = dragInfo;
        genro.dom.addClass(dojo.body(), 'drag_started');
    },
    setInDataTransfer:function(dataTransfer, k, v) {
        var v = convertToText(v);
        v = ((k.indexOf('text/') == 0) || (v[0] == '') || (v[0] == 'T')) ? v[1] : v[1] + '::' + v[0];
        dataTransfer.setData(k, v);
        if (genro.dom.dragDropPatch()) {
            genro.dom._transferObj[k] = v;
        }
    },
    setDragSourceInfo:function(dragInfo, dragValues, dragTags) {
        if (dragInfo.nodeId) {
            dragValues['sourceNode_nodeId:' + dragInfo.nodeId] = null;
        }
        if (dragInfo.sourceNode) {
            dragValues['sourceNode__id:' + dragInfo.sourceNode._id] = null;
            if (dragInfo.sourceNode.getAttributeFromDatasource('detachable')) {
                dragValues['sourceNode_detachable:true'] = null;
            }

        }
        if (dragInfo.dragmode) {
            dragValues['sourceNode_dragmode:' + dragInfo.dragmode] = null;
        }
        dragValues['sourceNode_page_id:' + genro.page_id] = null;
        if (dragTags) {
            dragValues['sourceNode_dragTags:' + dragTags] = null;
        }
    },
    getDragSourceInfo:function(dataTransfer) {
        var draggedTypes = genro.dom.dataTransferTypes(dataTransfer);
        var dt;
        var result = {};
        for (var i = 0; i < draggedTypes.length; i++) {
            if (draggedTypes[i].indexOf('sourceNode_') == 0) {
                dt = draggedTypes[i].slice(11).split(':');
                result[dt[0]] = dt[1];
            }
        }
        ;
        return result;
    },
    getFromDataTransfer:function(dataTransfer, k) {
        var value = genro.dom.dragDropPatch() ? (genro.dom._transferObj ? genro.dom._transferObj[k] : null) : dataTransfer.getData(k);
        return convertFromText(value);
    },
    dataTransferTypes:function(dataTransfer) {
        if (genro.dom.dragDropPatch()) {
            var dt = [];
            if (genro.dom._transferObj) {
                for (var k in genro.dom._transferObj) {
                    dt.push(k);
                }
            }
            for (var i = 0; i < dataTransfer.types.length; i++) {
                dt.push(dataTransfer.types[i]);
            }
            ;
            return dt;
        } else {
            return dataTransfer.types;
        }
        return dataTransfer.types;
    },
    onDragEnd:function(event) {
        genro.dom.outlineShape(null);
    },
    getEventModifiers:function(e) {
        var m = [];
        if (e.shiftKey) {
            m.push('Shift');
        }
        if (e.ctrlKey) {
            m.push('Ctrl');
        }
        if (e.altKey) {
            m.push('Alt');
        }
        if (e.metaKey) {
            m.push('Meta');
        }
        return m.join();
    },
    dragDropPatch:function() {
        return (genro.isChrome);
    },
    startTouchDevice:function() {
        document.body.ontouchmove = function(e) {
            e.preventDefault();
        };
        document.body.onorientationchange = function(e) {
            genro.setData('touch.orientation', window.orientation);
        };
        dojo.connect(document.body, 'gestureend', function(e) {
            genro.dom.logTouchEvent('gesture', e);
        });

    },
    logTouchEvent:function(path, e) {

        var b = '';
        for (var k in e) {
            b = b + k + ':' + e[k] + '<br/>';
        }
        genro.setData('touch.event.' + path, b);
    },
    scrollableTable:function(domnode, gridbag, kw) {
        var columns = kw.columns;
        var headers = kw.headers;
        var tblclass = kw.tblclass;
        var thead = '<thead><tr>';
        for (var k = 0; k < columns.length; k++) {
            thead = thead + "<th>" + headers[k] + "</th>";
        }
        thead = thead + "<th style='width:10px; background-color:transparent;'>&nbsp</th></thead>";
        var nodes = gridbag.getNodes();
        var item,r, value;
        var tbl = ["<tbody>"];
        for (var i = 0; i < nodes.length; i++) {
            r = "";
            item = nodes[i].attr;
            for (var k = 0; k < columns.length; k++) {
                value = item[columns[k]] || '&nbsp';
                r = r + "<td>" + genro.format(value, {date:'short'});
                +"</td>";
            }
            tbl.push("<tr id='" + nodes[i].label + "'>" + r + "</tr>");
        }
        tbl.push("</tbody>");
        var tbody = tbl.join('');
        var cbf = function(cgr) {

            var cgr_h = cgr ? '<colgroup>' + cgr + '<col width=10 /></colgroup>' : '';
            var cgr_b = cgr ? '<colgroup>' + cgr + '</colgroup>' : '';
            return '<div class="' + tblclass + '"><div><table>' + cgr_h + '' + thead + '</table></div><div style="overflow-y:auto;max-height:180px;"><table>' + cgr_b + tbody + '</table></div></div>';
        };
        domnode.innerHTML = cbf('');
        var cb = function() {
            var hdrtr = dojo.query('thead tr', domnode)[0].children;
            var bodytr = dojo.query('tbody tr', domnode);
            var bodytr_first = bodytr[0].children;
            var colgroup = "";
            for (var i = 0; i < bodytr_first.length; i++) {
                var wh = hdrtr[i].clientWidth;
                var wb = bodytr_first[i].clientWidth;
                var wt = wh > wb ? wh : wb;
                colgroup = colgroup + '<col width="' + wt + '"/>';
            }
            ;
            domnode.innerHTML = cbf(colgroup);
            dojo.style(domnode, {width:'auto'});
            var rows = dojo.query('tbody tr', domnode);
            for (var i = 0; i < rows.length; i++) {
                rows[i].item = nodes[i];
            }
            ;
        };
        setTimeout(cb, 1);
    },
    centerOn: function(what, where, onlyX, onlyY) {
        var whatDomNode = this.getDomNode(what);
        var whereDomNode = where ? this.getDomNode(where) : whatDomNode.parentNode;
        var viewport = dojo.coords(whereDomNode);
        var mb = dojo.marginBox(whatDomNode);
        var result = {};
        var style = whatDomNode.style;
        var whereposition = whereDomNode.style.position;
        var deltax = viewport.l;
        var deltay = viewport.t;
        //if (whereposition=='relative' || whereposition=='absolute'){
        //    deltax = deltax +viewport.x;
        //    deltay = deltay + viewport.y;
        //}
        if (!onlyY) {
            style.left = Math.floor((deltax + (viewport.w - mb.w) / 2)) + "px";
        }
        if (!onlyX) {
            style.top = Math.floor((deltay + (viewport.h - mb.h) / 2)) + "px";
        }

    },
    makeHiderLayer: function(parentId, kw) {
        var rootNode = parentId ? genro.nodeById(parentId) : genro.src.getNode();
        var default_kw = {'position':'absolute',top:'0',left:'0',right:'0','bottom':0,
            z_index:1000,background_color:'rgba(255,255,255,0.5)',id:parentId + '_hider'};
        var kw = objectUpdate(default_kw, kw);
        return rootNode._('div', kw).getParentNode();
    }

});