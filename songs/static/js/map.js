var map;
var markers = [];

var markers_id = [];

var edit_marker;

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
    center: new google.maps.LatLng(lat,lon),
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    streetViewControl:false,
    mapTypeControl:false
  };
  map = new google.maps.Map(document.getElementById('map_canvas'), myOptions); 
  markerCluster = new MarkerClusterer(map);
  google.maps.event.addListener(map, 'dragend', function(event){
    show();
  });
  google.maps.event.addListenerOnce(map, 'idle', function(event) {
    load_user_items()
    show();
  });
  google.maps.event.addListener(map, 'zoom_changed', function(event) {
    show();
  });
  google.maps.event.addListener(map, 'bounds_changed', function(event) {
    show();
  });


  // edition marker


  edit_marker = new google.maps.Marker()

  if(is_authenticated){
    google.maps.event.addListener(map, 'click', function(event){
      $('#id_position').val(event.latLng.toString());
      $('#input-search').val('');
      $('#open_modal').trigger('click');
      /*current_position = event.latLng
      edit_marker.setMap(map);
      edit_marker.setPosition(event.latLng);
      infowindow.open(map, edit_marker);
      */
    })
  }

  var content = '<form class="form-search"> '+
    '<label for="add-item-input">Search song:</label><input type="text" id="add-item-input" class="input-medium search-query">' +
    '</form>';

  var infowindow = new google.maps.InfoWindow({
    content: content,
    maxWidth:400
  });

  google.maps.event.addListener(infowindow, 'domready', function(event){
    $('#add-item-input').typeahead(typeahead_options);
    $('#add-item-input').focus()
  })

  google.maps.event.addListener(infowindow, 'closeclick', function(event){
    edit_marker.setMap(null);
  })

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
      //map: map,
      draggable: true,
      icon:icon_red,
    });
    markers.push(marker);
    $(this).data('marker', marker);
    $(marker).data('item_id', $(this).next().val());
    addEventsToMarker(this, marker);
  })
  /*
  $('.close').live('click', function(event){
    $(this).parent().find('*[name$=DELETE]').attr('checked', true);
    $(this).parent().find('.marker').data('marker').setMap(null);
    $(this).parent().hide();
  })
  */

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
      // don't work this.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);
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

function add_marker(position, form){
  var position = new google.maps.LatLng(position.lat(), position.lng())
  var marker = new google.maps.Marker({
      map:map,
      draggable:true,
      position: position
  })

  //$(ui.draggable).attr('data-original-title', 'click to center map on this track')
  //$(ui.draggable).parent().find('*[name$=position]').val(position.toString())
  form.find('*[name$=position]').data('marker', marker);
  $(marker).data('item_id', form.find('*[name$=item_id]').val());
  addEventsToMarker(form.find('*[name$=position]').get(0), marker);
  markers.push(marker);

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
function item_save_callback(data){
  console.log(data, data.item_js)
  item_js = jQuery.parseJSON(data.item_js)
  $('#item-list').prepend(data.html);
  item_data = item_js[0]
  show_item(item_data)
}

function item_delete_callback(data){
  console.log(data)
}

// shadow for map markers
var shadow_out = new google.maps.MarkerImage('/static/img/shadow_out.png', null, new google.maps.Point(0, 0), new google.maps.Point(0, 0), null);
var shadow_over = new google.maps.MarkerImage('/static/img/shadow_over.png', null, new google.maps.Point(0, 0), new google.maps.Point(0, 0), null)
var shadow_click = new google.maps.MarkerImage('/static/img/shadow_click.png', null, new google.maps.Point(0, 0), new google.maps.Point(0, 0), null)

var marker_current;
function update_current(marker){
  if(marker_current){
    marker_current.setShadow(shadow_out);
  }
  marker_current = marker
}

function show_item(data){
  if($.inArray(data.pk, markers_id) == -1){
    var re = /\((.*),\s(.*)\)/;
    var m = re.exec(data.fields.position);
    var lat = parseFloat(m[1]);
    var lng = parseFloat(m[2]);
    var json = jQuery.parseJSON(data.fields.json)
    var picture = new google.maps.MarkerImage(json.artist.picture, null, new google.maps.Point(0, 0), new google.maps.Point(-5, -5), new google.maps.Size(50, 50));
    var cover = new google.maps.MarkerImage(json.album.cover, null, new google.maps.Point(0, 0), new google.maps.Point(-5, -5), new google.maps.Size(50, 50));
    var marker = new google.maps.Marker({
      position: new google.maps.LatLng(lat,lng),
      //map: map,
      draggable: false,
      icon:picture,
      shadow:shadow_out, 
      id:data.pk
    });
    marker.data = data
    marker.picture = picture
    marker.cover = cover
    marker.json = json
    markers.push(marker)
    markerCluster.addMarker(marker)
    google.maps.event.addListener(marker, 'click', function(event){
      //TODO: add visualisation for play function
      playTrack(this.data.fields.item_id);
      this.setIcon(this.cover);
      this.setShadow(shadow_click);
      update_current(marker)
    })
    markers_id.push(data.pk);
    google.maps.event.addListener(marker, 'mouseover', function(event){
      if(this.getShadow().url != shadow_click.url){
        this.setIcon(this.cover);
        this.setShadow(shadow_over);
        this.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);
       }
    })
    google.maps.event.addListener(marker, 'mouseout', function(event){
      if(this.getShadow().url != shadow_click.url){
        this.setIcon(this.picture);
        this.setShadow(shadow_out);
      }
    })
  }
  // below we should hold id of currently displayed item 
  // to not reshow them
  //markers.push(marker);
}

function remove_items(data){
  
}


