var baseStopIcon = new GIcon(G_DEFAULT_ICON);
baseStopIcon.image = "/images/bus_stop.png"; //http://code.google.com/p/google-maps-icons/wiki/TransportationIcons
baseStopIcon.shadow = "/images/shadow.png";
baseStopIcon.iconSize = new GSize(20, 20);
baseStopIcon.shadowSize = new GSize(20, 20);
baseStopIcon.iconAnchor = new GPoint(16, 16);
baseStopIcon.infoWindowAnchor = new GPoint(5, 1);

var activeMarker = null;

function createStopMarker(stop) {
  var stopIcon = new GIcon(baseStopIcon);
  var markerOptions = { icon:stopIcon };
  var point = new GLatLng(stop[1], stop[2]);
  var marker = new GMarker(point, markerOptions);

  GEvent.addListener(marker, "click", function() {
	marker.openInfoWindowHtml('<b>' + stop[3] + '</b><br /><div id="infobox_details"><img src="/images/ajax-loader.gif" /></div>',
			{ maxWidth: 200 });
	$.get('/ajax/stop_details/' + stop[0] + '/', function(data) {
		if (marker == activeMarker) {
			iw = marker.openInfoWindowHtml('<b>' + stop[3] + '</b><br />' + data,
					{ maxWidth: 200 });
			screenshotPreview();
		}
	});
  });
  GEvent.addListener(marker, "infowindowopen", function() {
	  activeMarker = marker;
  });  
  GEvent.addListener(marker, "infowindowclose", function() {
	  activeMarker = null;
  });
  return marker;
}

function drawTrip(trip_id) {
	//remove poly & stops
	if (document.poly) {
		document.map.removeOverlay(document.poly);
	}
	
	if (trip_id) {
		$.ajax({
			url: '/ajax/get_poly/' + trip_id,
			type: 'GET',
			dataType: 'json',
			timeout: 3000,
			tryCount : 0,
			retryLimit : 3,
			success: function(jsonDATA) {
				if (jsonDATA.color) {
				    color = jsonDATA.color;
				} else {
					color = "#0000FF" 
				}
				
				//poly
				document.poly = GPolyline.fromEncoded({
					color: color,
					weight: 7,
					points: jsonDATA.points,
					levels: jsonDATA.levels,
					zoomFactor: 32,
					numLevels: 4
				});
				
				var bounds = document.poly.getBounds();
				document.map.setCenter(bounds.getCenter());
				document.map.setZoom(document.map.getBoundsZoomLevel(bounds));
				document.map.addOverlay(document.poly);
				
				//stops
				var stops = jsonDATA.stops;
				for(var i=0; i < stops.length; i++) {
					document.map.addOverlay(createStopMarker(stops[i]));
				}
			},
			error : function(xhr, textStatus, errorThrown ) {
				if (textStatus == 'timeout') {
					this.tryCount++;
					if (this.tryCount <= this.retryLimit) {
						//try again
						$.ajax(this);
						return;
					}
					alert('Não foi possível conectar-se ao servidor para baixar esta rota. Por favor, tente recarregar a página.');
					return;
				}
				if (xhr.status == 500) {
					alert('Oops! Houve um erro com o servidor. Desculpe!');
				} else {
					alert('Oops! Ocorreu um erro. Tente mais tarde, por favor.');
				}
			}
		});
	}
};

function createMap() {
  if (!GBrowserIsCompatible()) {
	alert('Desculpe, seu navegador não é compatível com o Google Maps API.');
	return;
  }

  document.map = new GMap2(document.getElementById("map_canvas"));
  document.map.setCenter(new GLatLng(-23.55258,	-46.731579), 12);
  document.map.addControl(new GSmallMapControl());
  document.map.addControl(new GMapTypeControl());
  
};
					
$(document).ready(function(){
	createMap();
	if (trip_id) {
		drawTrip(trip_id);
	}
});