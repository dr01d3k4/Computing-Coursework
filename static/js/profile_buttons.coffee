unless typeof String::endsWith is "function"
	String::endsWith = (suffix) -> @indexOf(suffix, @length - suffix.length) isnt -1



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
		dialogue = new Dialogue title: title
		return unless dialogue

		$.getJSON url, (data) ->
			# [{fullName: "Ben", username: "Ben", profileImage: ""}, {fullName: "Testy", username: "Test", profileImage: ""}, {fullName: "A", username: "a", profileImage: ""}]
			for user in data.users
				$userItem = $ "<div>"
				$userItem.addClass "user-item"

				$profileImage = $ "<img>"
				$profileImage.addClass "user-item-profile-image"
				$profileImage.attr "src", user.profileImage
				$profileImage.attr "alt", "No profile image"
				$userItem.append $profileImage

				$fullName = $ "<div>"
				$fullName.addClass "user-item-full-name"
				$fullName.text user.fullName
				$userItem.append $fullName

				$username = $ "<div>"
				$username.addClass "user-item-username"
				$username.text "@#{user.username}"
				$userItem.append $username

				$profileView = $ "<a>"
				$profileView.addClass "user-item-view"
				$profileView.attr "href", user.absoluteUrl
				$profileView.text "View"

				$userItem.append $profileView

				# $profileUrlMeta = $ "<div>"
				# $profileUrlMeta.addClass "invisible"
				# $profileUrlMeta.hide()

				$userItem.hide().appendTo(dialogue.$dialogueContent).slideDown(200) # dialogue.$dialogueContent.append $userItem



	$viewFollowersButton = $ "#profile-view-followers-button"
	$viewFollowersButton.click ->
		viewFollowersFollowedButtonClicked "#{if viewingSelf then 'Your' else wordToGenitiveCase viewingFirstName} Followers",
			"/social/api/get-followers/#{viewingUsername}"

	$viewFollowedButton = $ "#profile-view-followed-button"
	$viewFollowedButton.click ->
		viewFollowersFollowedButtonClicked "Who #{if viewingSelf then 'you' else viewingFirstName} follow#{unless viewingSelf then 's' else ''}",
			"/social/api/get-users-followed-by/#{viewingUsername}"


	# viewFollowersFollowedButtonClicked "Your followers", "/social/api/get-followers/#{viewingUsername}"