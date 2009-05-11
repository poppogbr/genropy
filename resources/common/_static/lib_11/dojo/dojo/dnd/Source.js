/*
	Copyright (c) 2004-2008, The Dojo Foundation
	All Rights Reserved.

	Licensed under the Academic Free License version 2.1 or above OR the
	modified BSD license. For more information on Dojo licensing, see:

		http://dojotoolkit.org/book/dojo-book-0-9/introduction/licensing
*/


if(!dojo._hasResource["dojo.dnd.Source"]){
dojo._hasResource["dojo.dnd.Source"]=true;
dojo.provide("dojo.dnd.Source");
dojo.require("dojo.dnd.Selector");
dojo.require("dojo.dnd.Manager");
dojo.declare("dojo.dnd.Source",dojo.dnd.Selector,{isSource:true,horizontal:false,copyOnly:false,skipForm:false,withHandles:false,accept:["text"],constructor:function(_1,_2){
dojo.mixin(this,dojo.mixin({},_2));
var _3=this.accept;
if(_3.length){
this.accept={};
for(var i=0;i<_3.length;++i){
this.accept[_3[i]]=1;
}
}
this.isDragging=false;
this.mouseDown=false;
this.targetAnchor=null;
this.targetBox=null;
this.before=true;
this.sourceState="";
if(this.isSource){
dojo.addClass(this.node,"dojoDndSource");
}
this.targetState="";
if(this.accept){
dojo.addClass(this.node,"dojoDndTarget");
}
if(this.horizontal){
dojo.addClass(this.node,"dojoDndHorizontal");
}
this.topics=[dojo.subscribe("/dnd/source/over",this,"onDndSourceOver"),dojo.subscribe("/dnd/start",this,"onDndStart"),dojo.subscribe("/dnd/drop",this,"onDndDrop"),dojo.subscribe("/dnd/cancel",this,"onDndCancel")];
},checkAcceptance:function(_5,_6){
if(this==_5){
return true;
}
for(var i=0;i<_6.length;++i){
var _8=_5.getItem(_6[i].id).type;
var _9=false;
for(var j=0;j<_8.length;++j){
if(_8[j] in this.accept){
_9=true;
break;
}
}
if(!_9){
return false;
}
}
return true;
},copyState:function(_b){
return this.copyOnly||_b;
},destroy:function(){
dojo.dnd.Source.superclass.destroy.call(this);
dojo.forEach(this.topics,dojo.unsubscribe);
this.targetAnchor=null;
},markupFactory:function(_c,_d){
_c._skipStartup=true;
return new dojo.dnd.Source(_d,_c);
},onMouseMove:function(e){
if(this.isDragging&&this.targetState=="Disabled"){
return;
}
dojo.dnd.Source.superclass.onMouseMove.call(this,e);
var m=dojo.dnd.manager();
if(this.isDragging){
var _10=false;
if(this.current){
if(!this.targetBox||this.targetAnchor!=this.current){
this.targetBox={xy:dojo.coords(this.current,true),w:this.current.offsetWidth,h:this.current.offsetHeight};
}
if(this.horizontal){
_10=(e.pageX-this.targetBox.xy.x)<(this.targetBox.w/2);
}else{
_10=(e.pageY-this.targetBox.xy.y)<(this.targetBox.h/2);
}
}
if(this.current!=this.targetAnchor||_10!=this.before){
this._markTargetAnchor(_10);
m.canDrop(!this.current||m.source!=this||!(this.current.id in this.selection));
}
}else{
if(this.mouseDown&&this.isSource){
var _11=this.getSelectedNodes();
if(_11.length){
m.startDrag(this,_11,this.copyState(dojo.dnd.getCopyKeyState(e)));
}
}
}
},onMouseDown:function(e){
if(this._legalMouseDown(e)&&(!this.skipForm||!dojo.dnd.isFormElement(e))){
this.mouseDown=true;
this.mouseButton=e.button;
dojo.dnd.Source.superclass.onMouseDown.call(this,e);
}
},onMouseUp:function(e){
if(this.mouseDown){
this.mouseDown=false;
dojo.dnd.Source.superclass.onMouseUp.call(this,e);
}
},onDndSourceOver:function(_14){
if(this!=_14){
this.mouseDown=false;
if(this.targetAnchor){
this._unmarkTargetAnchor();
}
}else{
if(this.isDragging){
var m=dojo.dnd.manager();
m.canDrop(this.targetState!="Disabled"&&(!this.current||m.source!=this||!(this.current.id in this.selection)));
}
}
},onDndStart:function(_16,_17,_18){
if(this.isSource){
this._changeState("Source",this==_16?(_18?"Copied":"Moved"):"");
}
var _19=this.accept&&this.checkAcceptance(_16,_17);
this._changeState("Target",_19?"":"Disabled");
if(_19&&this==_16){
dojo.dnd.manager().overSource(this);
}
this.isDragging=true;
},onDndDrop:function(_1a,_1b,_1c){
do{
if(this.containerState!="Over"){
break;
}
var _1d=this._normalizedCreator;
if(this!=_1a){
if(this.creator){
this._normalizedCreator=function(_1e,_1f){
return _1d.call(this,_1a.getItem(_1e.id).data,_1f);
};
}else{
if(_1c){
this._normalizedCreator=function(_20,_21){
var t=_1a.getItem(_20.id);
var n=_20.cloneNode(true);
n.id=dojo.dnd.getUniqueId();
return {node:n,data:t.data,type:t.type};
};
}else{
this._normalizedCreator=function(_24,_25){
var t=_1a.getItem(_24.id);
_1a.delItem(_24.id);
return {node:_24,data:t.data,type:t.type};
};
}
}
}else{
if(this.current&&this.current.id in this.selection){
break;
}
if(this.creator){
if(_1c){
this._normalizedCreator=function(_27,_28){
return _1d.call(this,_1a.getItem(_27.id).data,_28);
};
}else{
if(!this.current){
break;
}
this._normalizedCreator=function(_29,_2a){
var t=_1a.getItem(_29.id);
return {node:_29,data:t.data,type:t.type};
};
}
}else{
if(_1c){
this._normalizedCreator=function(_2c,_2d){
var t=_1a.getItem(_2c.id);
var n=_2c.cloneNode(true);
n.id=dojo.dnd.getUniqueId();
return {node:n,data:t.data,type:t.type};
};
}else{
if(!this.current){
break;
}
this._normalizedCreator=function(_30,_31){
var t=_1a.getItem(_30.id);
return {node:_30,data:t.data,type:t.type};
};
}
}
}
this._removeSelection();
if(this!=_1a){
this._removeAnchor();
}
if(this!=_1a&&!_1c&&!this.creator){
_1a.selectNone();
}
this.insertNodes(true,_1b,this.before,this.current);
if(this!=_1a&&!_1c&&this.creator){
_1a.deleteSelectedNodes();
}
this._normalizedCreator=_1d;
}while(false);
this.onDndCancel();
},onDndCancel:function(){
if(this.targetAnchor){
this._unmarkTargetAnchor();
this.targetAnchor=null;
}
this.before=true;
this.isDragging=false;
this.mouseDown=false;
delete this.mouseButton;
this._changeState("Source","");
this._changeState("Target","");
},onOverEvent:function(){
dojo.dnd.Source.superclass.onOverEvent.call(this);
dojo.dnd.manager().overSource(this);
},onOutEvent:function(){
dojo.dnd.Source.superclass.onOutEvent.call(this);
dojo.dnd.manager().outSource(this);
},_markTargetAnchor:function(_33){
if(this.current==this.targetAnchor&&this.before==_33){
return;
}
if(this.targetAnchor){
this._removeItemClass(this.targetAnchor,this.before?"Before":"After");
}
this.targetAnchor=this.current;
this.targetBox=null;
this.before=_33;
if(this.targetAnchor){
this._addItemClass(this.targetAnchor,this.before?"Before":"After");
}
},_unmarkTargetAnchor:function(){
if(!this.targetAnchor){
return;
}
this._removeItemClass(this.targetAnchor,this.before?"Before":"After");
this.targetAnchor=null;
this.targetBox=null;
this.before=true;
},_markDndStatus:function(_34){
this._changeState("Source",_34?"Copied":"Moved");
},_legalMouseDown:function(e){
if(!this.withHandles){
return true;
}
for(var _36=e.target;_36&&!dojo.hasClass(_36,"dojoDndItem");_36=_36.parentNode){
if(dojo.hasClass(_36,"dojoDndHandle")){
return true;
}
}
return false;
}});
dojo.declare("dojo.dnd.Target",dojo.dnd.Source,{constructor:function(_37,_38){
this.isSource=false;
dojo.removeClass(this.node,"dojoDndSource");
},markupFactory:function(_39,_3a){
_39._skipStartup=true;
return new dojo.dnd.Target(_3a,_39);
}});
}
