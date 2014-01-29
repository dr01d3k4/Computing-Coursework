unless typeof String.prototype.endsWith is "function"
	String.prototype.endsWith = (suffix) -> @indexOf(suffix, @length - suffix.length) isnt -1



wordToGenitiveCase = (word) -> "#{word}\'#{unless word.endsWith 's' then 's'}"


pluralPersonWord = (count) -> if count is 1 then "person" else "people"


$(document).ready ->
	$aboutButton = $ "#profile-about-more-button"
	$aboutMore = $ "#profile-about-more"



	updateFollowerCountLabel = ->
		$.ajax
			type: "get"
			url: "/social/api/get-follower-count/#{viewingUsername}/"
		.done (data) ->
			followerCount = parseInt data
			$aboutMore.find("#profile-about-follower-count").text("Followers: #{followerCount} #{pluralPersonWord followerCount}")

		$.ajax
			type: "get"
			url: "/social/api/get-followed-count/#{viewingUsername}/"
		.done (data) ->
			followedCount = parseInt data
			$aboutMore.find("#profile-about-followed-count").text("Follows: #{followedCount} #{pluralPersonWord followedCount}")



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
			$aboutMore.slideDown time, -> aboutSliding = no
			$aboutButton.text "Close"
		else
			$aboutMore.slideUp time, -> aboutSliding = no
			$aboutButton.text "About"


	$aboutButton.click ->
		setAboutMoreVisible not aboutVisible

	setAboutMoreVisible no, yes



	$followButton = $ "#profile-follow-button"
	clickedFollowButton = no

	$followButton.click ->
		return if clickedFollowButton
		clickedFollowButton = yes

		$.ajax
			type: "POST"
			url: "/social/follow/"
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



	viewFollowersFollowedButtonClicked = (title, url) ->
		$dialogueContent = createDialogue title: title
		return unless $dialogueContent
		$.getJSON url, (data) ->
			for user in data.users
				$dialogueContent.append user.fullName
				$dialogueContent.append "<br>"



	$viewFollowersButton = $ "#profile-view-followers-button"
	$viewFollowersButton.click ->
		viewFollowersFollowedButtonClicked "#{wordToGenitiveCase viewingFirstName} Followers",
			"/social/api/get-followers/#{viewingUsername}"

	$viewFollowedButton = $ "#profile-view-followed-button"
	$viewFollowedButton.click ->
		viewFollowersFollowedButtonClicked "Who #{if viewingSelf then 'you' else viewingFirstName} follow#{unless viewingSelf then 's' else ''}",
			"/social/api/get-users-followed-by/#{viewingUsername}"