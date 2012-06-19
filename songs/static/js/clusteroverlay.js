ClusterOverlay.prototype = new google.maps.OverlayView();

function ClusterOverlay(position, total, map) {

  // Now initialize all properties.
  this.position_ = position;
  this.map_ = map;
  this.total_ = total;
  this.imageStyle_ = this.getImageStyle();

  // We define a property to hold the image's
  // div. We'll actually create this div
  // upon receipt of the add() method so we'll
  // leave it null for now.
  this.div_ = null;

  // Explicitly call setMap() on this overlay
  this.setMap(this.map_);
}

ClusterOverlay.prototype.onAdd = function() {
  // Note: an overlay's receipt of onAdd() indicates that
  // the map's panes are now available for attaching
  // the overlay to the map via the DOM.

  // Create the DIV and set some basic attributes.
  var div = document.createElement('div');
  div.style.border = "none";
  div.style.borderWidth = "0px";
  div.style.position = "absolute";

  // Create an IMG element and attach it to the DIV.
  //var img = document.createElement("img");
  //img.src = this.imageStyle_['url'];
  //img.style.width = this.imageStyle_['size']+"px";
  //img.style.height = this.imageStyle_['size']+"px";
  //div.appendChild(img);
  var text = document.createElement("div");
  text.innerHTML = this.total_
  //UGLY
  text.style.cssText = "background-repeat: no-repeat ;padding-top:"+(this.imageStyle_['size']/2-10)+"px;text-align:center; background-image:url('"+this.imageStyle_['url']+"');font-weight:bold;"
  text.style.width = this.imageStyle_['size']+"px"
  text.style.height = this.imageStyle_['size']+"px"
  text.style.display = "block";

  div.appendChild(text);

  // Set the overlay's div_ property to this DIV
  this.div_ = div;

  // We add an overlay to a map via one of the map's panes.
  // We'll add this overlay to the overlayImage pane.
  var panes = this.getPanes();
  panes.overlayLayer.appendChild(div);
}

ClusterOverlay.prototype.draw = function() {
  var pos = this.getProjection().fromLatLngToDivPixel(this.position_);
  this.div_.style.top = (pos.y-this.imageStyle_['size']/2) + "px";
  this.div_.style.left = (pos.x-this.imageStyle_['size']/2) + "px";
  this.div_.style.width = this.imageStyle_['size']+"px";
  this.div_.style.height = this.imageStyle_['size']+"px";
}

ClusterOverlay.prototype.onRemove = function() {
  this.div_.parentNode.removeChild(this.div_);
  this.div_ = null;
}


ClusterOverlay.prototype.getImageStyle = function(){
  i = 0
  while(ClusterOverlay.CLUSTER_SIZES[i] < this.total_ && ClusterOverlay.CLUSTER_SIZES[i+1] > this.total_){
   i++;
  }
  return {'url':ClusterOverlay.IMAGE_PATH+i+ClusterOverlay.IMAGE_EXTENSION, 'size':ClusterOverlay.IMAGE_SIZES[i]}
}

ClusterOverlay.IMAGE_PATH = "/static/img/m";

ClusterOverlay.IMAGE_EXTENSION = ".png";

ClusterOverlay.IMAGE_SIZES = [53, 56, 66, 78, 90];

ClusterOverlay.CLUSTER_SIZES = [0, 10, 100, 5000, 10000, 20000, 20000000]
