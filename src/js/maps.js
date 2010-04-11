// Create a base icon for all of our markers that specifies the
// shadow, icon dimensions, etc.
var baseStopIcon = new GIcon(G_DEFAULT_ICON);
baseStopIcon.image = "http://labs.google.com/ridefinder/images/mm_20_blue.png"
baseStopIcon.shadow = "http://labs.google.com/ridefinder/images/mm_20_shadow.png";
baseStopIcon.iconSize = new GSize(12, 20);
baseStopIcon.shadowSize = new GSize(22, 20);
baseStopIcon.iconAnchor = new GPoint(6, 20);
baseStopIcon.infoWindowAnchor = new GPoint(5, 1);

// Creates a marker whose info window displays the letter corresponding
// to the given index.
function createStopMarker(index) {
  // Create a lettered icon for this point using our icon class
  var stopIcon = new GIcon(baseStopIcon);
  //letteredIcon.image = "http://www.google.com/mapfiles/marker" + letter + ".png";

  // Set up our GMarkerOptions object
  markerOptions = { icon:stopIcon };

  var point = new GLatLng(stops[index][2], stops[index][3]);

  var marker = new GMarker(point, markerOptions);

  GEvent.addListener(marker, "click", function() {
	marker.openInfoWindowHtml('<b>' + stops[index][0] + '</b><br />' + stops[index][1]);
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
				//poly
				document.poly = GPolyline.fromEncoded({
					color: "#0000FF",
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
				//for(var i=0; i < stops.length; i++) {
				//	document.map.addOverlay(createStopMarker(i));
				//}
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