// Content for 'nh-forge-extension.js'

function nhforgeext(viewer, options) {
  Autodesk.Viewing.Extension.call(this, viewer, options);
}

nhforgeext.prototype = Object.create(Autodesk.Viewing.Extension.prototype);
nhforgeext.prototype.constructor = nhforgeext;

Autodesk.Viewing.theExtensionManager.registerExtension('nh-forge Extension', nhforgeext);


nhforgeext.prototype.load = function() {
    this.onSelectionBinded = this.onSelectionEvent.bind(this);
    this.viewer.addEventListener(Autodesk.Viewing.SELECTION_CHANGED_EVENT, this.onSelectionBinded);

  return true;
};

 nhforgeext.prototype.unload = function() {
     this.viewer.removeEventListener(Autodesk.Viewing.SELECTION_CHANGED_EVENT, this.onSelectionBinded);
    this.onSelectionBinded = null;
    
  return true;
};

// Event hanlder for Autodesk.Viewing.SELECTION_CHANGED_EVENT
nhforgeext.prototype.onSelectionEvent = function(event) {
    var t = this.viewer.getSelection();
    //var domElem = document.getElementById('MySelectionValue');
    //domElem.innerText = t; //.length;
	
	// so we get the entire instance tree first, 
	var instanceTree = this.viewer.model.getData().instanceTree;
	
	// then go through it to find the node we have currently selected
	// start with the root
	var rootId = instanceTree.getRootId();
	// loop through all children until we find the one we're looking for - TODO allow for deeper nesting!
	var theOneWeWant=-1;
	
	instanceTree.enumNodeChildren(rootId, function(childId) 
	{
		instanceTree.enumNodeChildren(childId, function(childId2)
		{
			if (childId2==t[0])
			{
				theOneWeWant=childId;
			}
		})
	});
	
	// and then instead of that node we get its parent for which we get the properties
	// TODO: handle the case that the user select the right node in the first place in the model tree browser...
	
	this.viewer.getProperties(theOneWeWant,nhdatasuccess,nhdatafailed);
	//this.viewer.model.getBulkProperties(t,{propFilter: false, ignoreHidden: false },nhdatasuccess,nhdatafailed);
};


function nhrequest()
{
	 var domElem = document.getElementById('MySelectionValue');
	 
	 domElem.innerText += this.responseText;
}

nhdatasuccess = function(data)
{
	 var domElem = document.getElementById('MySelectionValue');
	 var v2=data.name.slice(0,-36)+" [uuid="+data.name.slice(-32)+"]";
	 //data.name=data.name.slice(0,-36);
	 var uuid=data.name.slice(-32);
	 
	 var req=new XMLHttpRequest();
	 req.addEventListener("load",nhrequest);
	 req.open("GET","http://localhost:81/get_data.php?uuid="+uuid);
	 req.send();
	 
	 domElem.innerText = v2;
}

nhdatafailed = function(data)
{
	 var domElem = document.getElementById('MySelectionValue');
	 domElem.innerText = "empty selection";	
}