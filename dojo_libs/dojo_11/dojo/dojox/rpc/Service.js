/*
	Copyright (c) 2004-2008, The Dojo Foundation
	All Rights Reserved.

	Licensed under the Academic Free License version 2.1 or above OR the
	modified BSD license. For more information on Dojo licensing, see:

		http://dojotoolkit.org/book/dojo-book-0-9/introduction/licensing
*/


if(!dojo._hasResource["dojox.rpc.Service"]){
dojo._hasResource["dojox.rpc.Service"]=true;
dojo.provide("dojox.rpc.Service");
dojo.require("dojo.AdapterRegistry");
dojo.declare("dojox.rpc.Service",null,{constructor:function(_1,_2){
var _3;
var _4=this;
function processSmd(_5){
_5._baseUrl=new dojo._Url(location.href,_3||".")+"";
_4._smd=_5;
for(var _6 in _4._smd.services){
_4[_6]=_4._generateService(_6,_4._smd.services[_6]);
}
};
if(_1){
if((dojo.isString(_1))||(_1 instanceof dojo._Url)){
if(_1 instanceof dojo._Url){
_3=_1+"";
}else{
_3=_1;
}
var _7=dojo._getText(_3);
if(!_7){
throw new Error("Unable to load SMD from "+_1);
}else{
processSmd(dojo.fromJson(_7));
}
}else{
processSmd(_1);
}
}
if(_2){
this._options=_2;
}
this._requestId=0;
},_generateService:function(_8,_9){
if(this[_9]){
throw new Error("WARNING: "+_8+" already exists for service. Unable to generate function");
}
_9.name=_8;
var _a=dojo.hitch(this,"_executeMethod",_9);
var _b=dojox.rpc.transportRegistry.match(_9.transport||this._smd.transport);
if(_b.getExecutor){
_a=_b.getExecutor(_a,_9,this);
}
var _c=_9.returns||(_9._schema={});
_c._idPrefix=_8+"/";
dojox.rpc.services[_8]=_a;
_c._service=_a;
_a.serviceName=_8;
_a._schema=_c;
return _a;
},_executeMethod:function(_d){
var _e=[];
var i;
for(i=1;i<arguments.length;i++){
_e.push(arguments[i]);
}
var smd=this._smd;
if(_d.parameters&&_d.parameters[0]&&_d.parameters[0].name&&(_e.length==1)&&dojo.isObject(_e[0])){
_e=_e[0];
if(smd.parameters&&smd.parameters[0]){
for(i=0;i<smd.parameters.length;i++){
if(smd.parameters[i]["name"]&&smd.parameters[i]["default"]){
_e[smd.parameters[i]["name"]]=smd.parameters[i]["default"];
}
}
}
}
if(dojo.isObject(this._options)){
_e=dojo.mixin(_e,this._options);
}
var _11=_d.envelope||smd.envelope||"NONE";
var _12=dojox.rpc.envelopeRegistry.match(_11);
var _13=_d._schema||_d.returns;
var _14=_12.serialize.apply(this,[smd,_d,_e]);
var _15=(_d.contentType||smd.contentType||_14.contentType);
var _16=(_15+"").match(/application\/json/);
dojo.mixin(_14,{sync:dojox.rpc._sync,handleAs:_16?"json":"text",contentType:_15,target:_14.target||dojox.rpc.getTarget(smd,_d),transport:_d.transport||smd.transport||_14.transport,envelope:_d.envelope||smd.envelope||_14.envelope,timeout:_d.timeout||smd.timeout,callbackParamName:_d.callbackParamName||smd.callbackParamName,preventCache:_d.preventCache||smd.preventCache});
var _17=(_d.restMethod||dojox.rpc.transportRegistry.match(_14.transport).fire).call(this,_14);
_17.addBoth(dojo.hitch(this,function(_18){
_18=_12.deserialize.call(this,_16?dojox.rpc.resolveJson(_18,_13):_18);
return _18;
}));
return _17;
}});
dojox.rpc.getTarget=function(smd,_1a){
var _1b=smd._baseUrl;
if(smd.target){
_1b=new dojo._Url(_1b,smd.target)+"";
}
if(_1a.target){
_1b=new dojo._Url(_1b,_1a.target)+"";
}
return _1b;
};
dojox.rpc.toNamed=function(_1c,_1d,_1e){
var i;
if(!dojo.isArray(_1d)){
if(_1e){
for(i=0;i<_1c.parameters.length;i++){
if((!_1c.parameters[i].optional)&&(!_1d[_1c.parameters[i].name])){
throw new Error("Optional Parameter '"+_1c.parameters[i].name+"' not supplied to "+_1c.name);
}
}
for(var x in _1d){
var _21=false;
for(i=0;i<_1c.parameters.length;i++){
if(_1c.parameters[i].name==x){
_21=true;
}
}
if(!_21){
delete _1d[x];
}
}
}
return _1d;
}
var _22={};
for(i=0;i<_1c.parameters.length;i++){
_22[_1c.parameters[i].name]=_1d[i];
}
return _22;
};
dojox.rpc.toOrdered=function(_23,_24){
if(dojo.isArray(_24)){
return _24;
}
var _25=[];
for(var i=0;i<_23.parameters.length;i++){
_25.push(_24[_23.parameters[i].name]);
}
return _25;
};
dojox.rpc.transportRegistry=new dojo.AdapterRegistry(true);
dojox.rpc.envelopeRegistry=new dojo.AdapterRegistry(true);
dojox.rpc.envelopeRegistry.register("URL",function(str){
return str=="URL";
},{serialize:function(smd,_29,_2a){
var d=dojo.objectToQuery(dojox.rpc.toNamed(_29,_2a,_29.strictParameters||smd.strictParameters));
return {data:d,transport:"POST"};
},deserialize:function(_2c){
return _2c;
}});
dojox.rpc.envelopeRegistry.register("JSON",function(str){
return str=="JSON";
},{serialize:function(smd,_2f,_30){
var d=dojox.rpc.toJson(dojox.rpc.toNamed(_2f,_30,_2f.strictParameters||smd.strictParameters));
return {data:d,contentType:"application/json"};
},deserialize:function(_32){
return _32;
}});
dojox.rpc.envelopeRegistry.register("PATH",function(str){
return str=="PATH";
},{serialize:function(smd,_35,_36){
var i;
var _38=dojox.rpc.getTarget(smd,_35);
if(dojo.isArray(_36)){
for(i=0;i<_36.length;i++){
_38+="/"+_36[i];
}
}else{
for(i in _36){
_38+="/"+i+"/"+_36[i];
}
}
return {data:"",target:_38};
},deserialize:function(_39){
return _39;
}});
dojox.rpc.transportRegistry.register("POST",function(str){
return str=="POST";
},{fire:function(r){
r.url=r.target;
r.postData=r.data;
return dojo.rawXhrPost(r);
}});
dojox.rpc.transportRegistry.register("GET",function(str){
return str=="GET";
},{fire:function(r){
r.url=r.target+(r.data?"?"+r.data:"");
r.preventCache=r.preventCache||true;
return dojo.xhrGet(r);
}});
dojox.rpc.transportRegistry.register("JSONP",function(str){
return str=="JSONP";
},{fire:function(r){
r.url=r.target+((r.target.indexOf("?")==-1)?"?":"&")+r.data,r.callbackParamName=r.callbackParamName||"callback";
return dojo.io.script.get(r);
}});
dojox.rpc.services={};
if(!dojox.rpc.toJson){
dojox.rpc.toJson=function(){
return dojo.toJson.apply(dojo,arguments);
};
dojox.rpc.fromJson=function(){
return dojo.fromJson.apply(dojo,arguments);
};
dojox.rpc.resolveJson=function(it){
return it;
};
}
}
