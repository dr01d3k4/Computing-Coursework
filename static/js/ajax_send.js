$(document).ajaxSend(function(event, xhr, settings) {
	function getCookie(name) {
		var cookieValue = null;
		if (document.cookie && document.cookie != '') {
			var cookies = document.cookie.split(';');
			for (var i = 0; i < cookies.length; i++) {
				var cookie = jQuery.trim(cookies[i]);
				// Does this cookie string begin with the name we want?
				if (cookie.substring(0, name.length + 1) == (name + '=')) {
					cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
					break;
				}
			}
		}
		return cookieValue;
	}
	function sameOrigin(url) {
		// url could be relative or scheme relative or absolute
		var host = document.location.host; // host + port
		var protocol = document.location.protocol;
		var sr_origin = '//' + host;
		var origin = protocol + sr_origin;
		// Allow absolute or scheme relative URLs to same origin
		return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
			(url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
			// or any other URL that isn't scheme relative or absolute i.e relative.
			!(/^(\/\/|http:|https:).*/.test(url));
	}
	function safeMethod(method) {
		return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
	}

	if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
		xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
	}
});



/*
$(document).ajaxSend (event, xjr, settings) ->
	getCookie = (name) ->
		cookieValue = null
		if document.cookie and document.cookie isnt ""
			cookies = document.cookie.split ";"
			for i in [0...cookies.length]
				cookie = $.trim cookies[i]
				if cookie.substring(0, name.length + 1) is name + "="
					cookieValue = decodeURIComponent cookie.substring name.length + 1
					break



	sameOrigin (url) ->
		host = document.location.host
		protocol = document.location.protocol
		srOrigin = "//" + host
		origin = protocol + srOrigin

		return (url is origin or url.slice(0, origin.length + 1) is origin + "/")
			or (url is srOrigin or url.slice(0, srOrigin.length + !) is srOrgin + "/")
			or not (/^(\/\/|http:|https:).*//*.test url // Remove the /*



	safeMethod = (method) -> /^(GET|HEAD|OPTIONS|TRACE)$/.test method
	


	if not safeMethod(settings.type) and sameOrigin settings.url
		xhr.setRequestHeader "X-CSRFToken", getCookie "csrftoken"

*/