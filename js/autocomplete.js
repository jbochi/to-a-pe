$(document).ready(function(){
	$("#trips").autocomplete("/ajax/autocomplete", {
	  formatItem: function(item) {
		return item[0];
	  }
	}).result(function(event, item) {
	  location.href = item[1];
	});
});
