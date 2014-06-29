$(document).ready ->
	$logoutButton = $ "#logout-button"
	$logoutButton.click ->
		$.ajax
			type: "POST"
			url: "/api/logout/"
		.done (data) ->
			window.location.href = "/"