/*
	Copyright (c) 2004-2008, The Dojo Foundation
	All Rights Reserved.

	Licensed under the Academic Free License version 2.1 or above OR the
	modified BSD license. For more information on Dojo licensing, see:

		http://dojotoolkit.org/book/dojo-book-0-9/introduction/licensing
*/


if(!dojo._hasResource["dijit.layout._LayoutWidget"]){
dojo._hasResource["dijit.layout._LayoutWidget"]=true;
dojo.provide("dijit.layout._LayoutWidget");
dojo.require("dijit._Widget");
dojo.require("dijit._Container");
dojo.declare("dijit.layout._LayoutWidget",[dijit._Widget,dijit._Container,dijit._Contained],{isLayoutContainer:true,postCreate:function(){
dojo.addClass(this.domNode,"dijitContainer");
},startup:function(){
if(this._started){
return;
}
dojo.forEach(this.getChildren(),function(_1){
_1.startup();
});
if(!this.getParent||!this.getParent()){
this.resize();
this.connect(window,"onresize",function(){
this.resize();
});
}
this.inherited(arguments);
},resize:function(_2){
var _3=this.domNode;
if(_2){
dojo.marginBox(_3,_2);
if(_2.t){
_3.style.top=_2.t+"px";
}
if(_2.l){
_3.style.left=_2.l+"px";
}
}
var mb=dojo.mixin(dojo.marginBox(_3),_2||{});
this._contentBox=dijit.layout.marginBox2contentBox(_3,mb);
this.layout();
},layout:function(){
}});
dijit.layout.marginBox2contentBox=function(_5,mb){
var cs=dojo.getComputedStyle(_5);
var me=dojo._getMarginExtents(_5,cs);
var pb=dojo._getPadBorderExtents(_5,cs);
return {l:dojo._toPixelValue(_5,cs.paddingLeft),t:dojo._toPixelValue(_5,cs.paddingTop),w:mb.w-(me.w+pb.w),h:mb.h-(me.h+pb.h)};
};
(function(){
var _a=function(_b){
return _b.substring(0,1).toUpperCase()+_b.substring(1);
};
var _c=function(_d,_e){
_d.resize?_d.resize(_e):dojo.marginBox(_d.domNode,_e);
dojo.mixin(_d,dojo.marginBox(_d.domNode));
dojo.mixin(_d,_e);
};
dijit.layout.layoutChildren=function(_f,dim,_11){
dim=dojo.mixin({},dim);
dojo.addClass(_f,"dijitLayoutContainer");
_11=dojo.filter(_11,function(_12){
return _12.layoutAlign!="client";
}).concat(dojo.filter(_11,function(_13){
return _13.layoutAlign=="client";
}));
dojo.forEach(_11,function(_14){
var elm=_14.domNode,pos=_14.layoutAlign;
var _17=elm.style;
_17.left=dim.l+"px";
_17.top=dim.t+"px";
_17.bottom=_17.right="auto";
dojo.addClass(elm,"dijitAlign"+_a(pos));
if(pos=="top"||pos=="bottom"){
_c(_14,{w:dim.w});
dim.h-=_14.h;
if(pos=="top"){
dim.t+=_14.h;
}else{
_17.top=dim.t+dim.h+"px";
}
}else{
if(pos=="left"||pos=="right"){
_c(_14,{h:dim.h});
dim.w-=_14.w;
if(pos=="left"){
dim.l+=_14.w;
}else{
_17.left=dim.l+dim.w+"px";
}
}else{
if(pos=="client"){
_c(_14,dim);
}
}
}
});
};
})();
}
