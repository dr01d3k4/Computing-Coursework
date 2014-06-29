unless typeof String::endsWith is "function"
	String::endsWith = (suffix) -> @indexOf(suffix, @length - suffix.length) isnt -1



wordToGenitiveCase = (word) -> "#{word}\'#{unless word.endsWith 's' then 's'}"



pluralPersonWord = (count) -> if count is 1 then "person" else "people"



$(document).ready ->
	$aboutMoreButton = $ "#profile-about-more-button"
	$aboutMore = $ "#profile-about-more"
	$aboutMoreUl = $aboutMore.children "ul"



	updateFollowerCountLabel = ->
		$.ajax
			type: "get"
			url: "/api/get-follower-count/#{viewingUsername}/"
		.done (data) ->
			followerCount = parseInt data
			$aboutMore.find("#profile-about-follower-count").text("Followed by #{followerCount} #{pluralPersonWord followerCount}")

		$.ajax
			type: "get"
			url: "/api/get-followed-count/#{viewingUsername}/"
		.done (data) ->
			followedCount = parseInt data
			$aboutMore.find("#profile-about-followed-count").text("Follows #{followedCount} #{pluralPersonWord followedCount}")



	aboutSlideTime = 150
	aboutVisible = no
	aboutSliding = no


	setAboutMoreVisible = (visible, instant = no) ->
		return if aboutSliding

		updateFollowerCountLabel() if visible

		aboutVisible = visible
		aboutSliding = yes
		time = if instant
			0
		else
			aboutSlideTime

		if aboutVisible
			$aboutMoreUl.slideDown time, -> aboutSliding = no
			$aboutMoreButton.text "Close"
		else
			$aboutMoreUl.slideUp time, -> aboutSliding = no
			$aboutMoreButton.text "About"


	$aboutMoreButton.click ->
		setAboutMoreVisible not aboutVisible

	setAboutMoreVisible no, yes



	$followButton = $ "#profile-follow-button"
	clickedFollowButton = no

	$followButton.click ->
		return if clickedFollowButton
		clickedFollowButton = yes

		$.ajax
			type: "POST"
			url: "/api/toggle-follows/"
			data: followUser: viewingUsername
		.done (data) ->
			if data.toLowerCase() is "true"
				$followButton.addClass "profile-follow-button-followed"
				$followButton.text "Followed!"
			else
				$followButton.removeClass "profile-follow-button-followed"
				$followButton.text "Follow"

			updateFollowerCountLabel()

			clickedFollowButton = no