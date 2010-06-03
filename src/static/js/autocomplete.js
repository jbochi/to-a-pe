$(document).ready(function(){
	$.ajax({
		  url: "/ajax/autocomplete",
		  dataType: "json",
		  success: 	function(jsonDATA) {
			$("#trips").autocomplete(jsonDATA, {
				matchContains: true,
				formatItem: function(item) {
					return item.text;
				}
			}).result(function(event, item) {
				location.href = item.url;
			});
		  }
	});
});
