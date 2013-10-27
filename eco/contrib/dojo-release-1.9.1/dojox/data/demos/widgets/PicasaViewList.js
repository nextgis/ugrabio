//>>built
define("dojox/data/demos/widgets/PicasaViewList",["dijit","dojo","dojox","dojo/require!dijit/_Templated,dijit/_Widget,dojox/data/demos/widgets/PicasaView"],function(_1,_2,_3){
_2.provide("dojox.data.demos.widgets.PicasaViewList");
_2.require("dijit._Templated");
_2.require("dijit._Widget");
_2.require("dojox.data.demos.widgets.PicasaView");
_2.declare("dojox.data.demos.widgets.PicasaViewList",[_1._Widget,_1._Templated],{templateString:_2.cache("dojox","data/demos/widgets/templates/PicasaViewList.html","<div dojoAttachPoint=\"list\"></div>\n\n"),listNode:null,postCreate:function(){
this.fViewWidgets=[];
},clearList:function(){
while(this.list.firstChild){
this.list.removeChild(this.list.firstChild);
}
for(var i=0;i<this.fViewWidgets.length;i++){
this.fViewWidgets[i].destroy();
}
this.fViewWidgets=[];
},addView:function(_4){
var _5=new _3.data.demos.widgets.PicasaView(_4);
this.fViewWidgets.push(_5);
this.list.appendChild(_5.domNode);
}});
});
