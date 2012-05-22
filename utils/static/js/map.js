var map;
var markers = [];

var markers_id = []


$(document).ready(function() {

  (function ($) {
   $.fn.liveDraggable = function (opts) {
      this.live("mouseover", function() {
         if (!$(this).data("init")) {
            $(this).data("init", true).draggable(opts);
         }
      });
      return $();
   };
  }(jQuery));

  $('.drag').liveDraggable({helper:"clone"})

  var myOptions = {
    zoom: 8,
    center: new google.maps.LatLng({{ lat }}, {{ lon }}),
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    streetViewControl:false,
    mapTypeControl:false
  };
  map = new google.maps.Map(document.getElementById('map_canvas'), myOptions); 

  google.maps.event.addListener(map, 'dragend', function(event){
    show();
  });
  google.maps.event.addListenerOnce(map, 'idle', function(event) {
    show();
  });
  google.maps.event.addListener(map, 'zoom_changed', function(event) {
    show();
  });
  google.maps.event.addListener(map, 'bounds_changed', function(event) {
    show();
  });


  var overlay = new google.maps.OverlayView();
  overlay.draw = function() {};
  overlay.setMap(map);

  $('.marker').each(function(){
    var re = /\((.*),\s(.*)\)/;
    var m = re.exec($(this).val());
    var lat = parseFloat(m[1]);
    var lng = parseFloat(m[2]);
    var marker = new google.maps.Marker({
      position: new google.maps.LatLng(lat,lng),
      map: map,
      draggable: true,
      icon:icon_red,
    });
    markers.push(marker);
    $(this).data('marker', marker);
    $(marker).data('item_id', $(this).next().val());
    addEventsToMarker(this, marker);
  })

  $('.close').live('click', function(event){
    $(this).parent().find('*[name$=DELETE]').attr('checked', true);
    $(this).parent().find('.marker').data('marker').setMap(null);
    $(this).parent().hide();
  })

	$('.well:not(.alert-success)')
	.live('mouseover', function(event){
		// change current form style
		$(this).addClass('alert-info');
		try{
			var current_maker = $(this).find('.marker').data('marker');
			// show marker linked to form on map
			current_maker.setIcon(icon_blue);
		}
		catch(err){
		
		}
	})
	.live('mouseout', function(event){
		$(this).removeClass('alert-info');
		try{
			var current_maker = $(this).find('.marker').data('marker');
			current_maker.setIcon(icon_red);			
		}
		catch(err){
			
		}
	})
	$('.well:not(.alert-success)').find('i.icon-map-marker').live('click', function(event){
		// center map
		try{
			var current_maker = $(this).parent().find('.marker').data('marker');
			map.setCenter(current_maker.getPosition())
		}
		catch(err){
		}	
	})


  $("#map_canvas").droppable({
    drop: function(event, ui){
      var x = ui.offset.left-$('#map_canvas').offset().left
      var y = ui.offset.top-$('#map_canvas').offset().top
      var point= new google.maps.Point(x, y);
      var location= overlay.getProjection().fromContainerPixelToLatLng(point);
      var position = new google.maps.LatLng(location.lat(), location.lng())
      var marker = new google.maps.Marker({
        map:map,
        draggable:true,
        position: position
      })
      $(ui.draggable).attr('data-original-title', 'click to center map on this track')
      $(ui.draggable).parent().find('*[name$=position]').val(position.toString())
      $(ui.draggable).parent().find('*[name$=position]').data('marker', marker);
      $(marker).data('item_id', $(ui.draggable).parent().find('*[name$=item_id]').val());
      addEventsToMarker($(ui.draggable).parent().find('*[name$=position]').get(0), marker);
      markers.push(marker);
    }
  })
  var geocoder = new google.maps.Geocoder();
  $('#location-input').keyup(function(evt){
    var address = $(this).val();
    if (geocoder) {
      geocoder.geocode({ 'address': address, 'region':'FR'}, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
          var lon = results[0].geometry.location.lng()
          var lat = results[0].geometry.location.lat()
          initialLocation = new google.maps.LatLng(lat,lon);
          map.setCenter(initialLocation);
          map.setZoom(10);
        }
      });
    }
  });

  // play functions
  $('i.icon-play').live('click', function(event){
    $(this).parent().removeClass('alert-info')
    playTrack($(this).parent().find('*[id$=item_id]').val())
    try{
		var current_maker = $(this).parent().find('.marker').data('marker');
		map.setCenter(current_maker.getPosition())
	}
		catch(err){
	}
  })

})

//
addEventsToMarker = function(field, marker){
  var self = field;
  google.maps.event.addListener(marker, 'dragend', function(event){
    $(self).val(event.latLng.toString());
  })
  google.maps.event.addListener(marker, 'mouseover', function(event){
    $(self).parent('.well').addClass('alert-info');
    if($(self).parent('.well').hasClass('alert-success')){
    }else{
      this.setIcon(icon_blue);
    }
  })
  google.maps.event.addListener(marker, 'mouseout', function(event){
    $(self).parent('.well').removeClass('alert-info');
    if($(self).parent('.well').hasClass('alert-success')){
    }else{
      this.setIcon(icon_red);
    }
  })
  google.maps.event.addListener(marker, 'click', function(event){
    $(self).parent('.well').removeClass('alert-info').addClass('alert-success');
    playTrack($(this).data('item_id'))
  })
}


// localize function
localizeMe = function(){
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
    initialLocation = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
    map.setCenter(initialLocation);
    map.setZoom(10);
    });
  }
}


// show current items

show = function(){
  Dajaxice.utils.get_items(items_callback, {'zone':map.getBounds().toString()});
}

function items_callback(data){
  if(data==Dajaxice.EXCEPTION){
    //alert('Error! Something happens!');
  }
  else{
    // TODO: below to remove unseend items
    var current_items = []
    for(i in data){
      show_item(data[i])
      current_items.push(data[i].pk)
      //TODO : remove unseen instances
    }
  }
}


function show_item(data){
  if($.inArray(data.pk, markers_id) == -1){
    var re = /\((.*),\s(.*)\)/;
    var m = re.exec(data.fields.position);
    var lat = parseFloat(m[1]);
    var lng = parseFloat(m[2]);
    var marker = new google.maps.Marker({
      position: new google.maps.LatLng(lat,lng),
      map: map,
      draggable: false,
      //title: 
      //icon:icon_red,
    });
    marker.data = data
    markers.push(marker)
    google.maps.event.addListener(marker, 'click', function(event){
      //TODO: add visualisation for play function
      playTrack(this.data.fields.item_id);
      this.setIcon(icon_green);
    })
    markers_id.push(data.pk)
    google.maps.event.addListener(marker, 'mouseover', function(event){
      if(this.getIcon() != '/static/img/green-dot.png'){
        this.setIcon(icon_blue);
       }
    })
    google.maps.event.addListener(marker, 'mouseout', function(event){
      if(this.getIcon() != '/static/img/green-dot.png'){
        this.setIcon(icon_red);
      }
    })
  }
  // below we should hold id of currently displayed item 
  // to not reshow them
  //markers.push(marker);
}

function remove_items(data){
  
}


