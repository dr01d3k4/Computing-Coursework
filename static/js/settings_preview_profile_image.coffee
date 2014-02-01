$(document).ready ->
	$imageField = $("#profile-image-field")
	$imageView = $("#profile-image-view")

	$imageField.change ->
		$input = this

		if $input.files and $input.files[0]
			reader = new FileReader()

			reader.onload = (e) ->
				$imageView.attr "src", e.target.result

			reader.readAsDataURL $input.files[0]