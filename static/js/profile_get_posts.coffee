$(document).ready ->
	$("html, body").animate scrollTop: "0px"


	GET_POSTS_LENGTH = 10
	gotAmount = 0
	UPDATE_TIME_SECONDS = 60
	WINDOW_BOTTOM_LOAD_NEW_POSTS_SCROLL = 64
	topLayerVisiblePosts = [ ]

	isTopLayerVisiblePost = (id) ->
		for i in topLayerVisiblePosts
			if id is i
				return yes
		return no



	$postTopLayer = $ "#post-top-layer"


	SHOW_TIME = 250
	NO_POSTS_TIME = 600
	viewRepliesPressed = no

	maximumReplyLengthCharacters = 255

	$postReplyBox = $ "<div>"
	$postReplyBox.attr "id", "post-reply-box"
	$postReplyBoxAppendedToButton = null
	postReplyBoxAppendedToId = -1

	$postReplyBoxContent = $ "<div>"
	$postReplyBoxContent.attr "id", "post-reply-box-content"

	$postReplyBoxTextBox = $ "<textarea>"
	$postReplyBoxTextBox.attr "id", "post-reply-box-text-box"
	$postReplyBoxTextBox.attr "type", "text"
	$postReplyBoxTextBox.attr "placeholder", "Type a reply"
	$postReplyBoxTextBox.attr "autofocus", "autofocus"
	$postReplyBoxTextBox.attr "maxlength", maximumReplyLengthCharacters
	$postReplyBoxTextBox.attr "name", "reply"
	$postReplyBoxTextBox.attr "spellcheck", "true"
	$postReplyBoxTextBox.attr "autocorrect", "on"
	$postReplyBoxTextBox.attr "autocapitalize", "on"
	$postReplyBoxContent.append $postReplyBoxTextBox

	$postReplyBox.append $postReplyBoxContent

	$postReplyBoxFooter = $ "<div>"
	$postReplyBoxFooter.attr "id", "post-reply-box-footer"

	$postReplyBoxCharactersRemaining = $ "<span>"
	$postReplyBoxCharactersRemaining.addClass "post-small-text-left"
	$postReplyBoxCharactersRemaining.text "255 characters remaining"
	$postReplyBoxFooter.append $postReplyBoxCharactersRemaining

	$postReplyBoxPostContainer = $ "<div>"
	$postReplyBoxPostContainer.attr "id", "post-reply-box-post-container"

	$postReplyBoxPost = $ "<div>"
	$postReplyBoxPost.attr "id", "post-reply-box-post"
	$postReplyBoxPost.text "Post"

	$postReplyBoxPostContainer.append $postReplyBoxPost
	$postReplyBoxFooter.append $postReplyBoxPostContainer

	$postReplyBox.append $postReplyBoxFooter



	$postReplyBoxTextBox.bind "input propertychange", ->
		charactersRemaining = maximumReplyLengthCharacters - this.value.length
		$postReplyBoxCharactersRemaining.text "#{charactersRemaining} character#{if charactersRemaining isnt 1 then 's' else ''} remaining"

		start = 50
		if charactersRemaining < start
			red = Math.floor(255 * (start - charactersRemaining) / start)
			$postReplyBoxCharactersRemaining.css "color", "rgb(#{red}, 0, 0)"
		else
			$postReplyBoxCharactersRemaining.css "color", "black"



	closePostReplyBox = ($button) ->
		return unless $postReplyBoxAppendedToButton?
		$postReplyBox.slideUp SHOW_TIME, -> $postReplyBox.detach()
		if postReplyBoxAppendedToId is "NEW"
			$button.text "Post a new post"
		else
			$button.text "Post reply"

		$postReplyBoxAppendedToButton = null
		postReplyBoxAppendedToId = -1



	onPostReplyOpenClicked = ->
		$button = $(this)
		id = $button.parent().parent().data("post-id")

		if $postReplyBoxAppendedToButton?.is $button
			closePostReplyBox $button

		else
			if $postReplyBoxAppendedToButton?
				if postReplyBoxAppendedToId is "NEW"
					$postReplyBoxAppendedToButton.text "Post a new post"
				else
					$postReplyBoxAppendedToButton.text "Post reply"

			$button.text "Close"

			$postReplyBoxAppendedToButton = $button
			postReplyBoxAppendedToId = id

			$postReplyBox.slideUp SHOW_TIME, ->
				$postReplyBox.appendTo($button.parent().parent()).hide().slideDown SHOW_TIME, ->
					$postReplyBoxTextBox.focus()



	postReplyClicked = no
	onPostReplyClicked = ->
		return if postReplyClicked
		postReplyClicked = yes

		$button = $(this)

		postContent = $postReplyBoxTextBox.val()
		if postContent.length is 0
			$blankPost = $ "<span>"
			$blankPost.addClass "post-small-text-right"
			$blankPost.text "Please enter a reply"
			$blankPost.hide()
			$button.after $blankPost
			$blankPost.show(SHOW_TIME).delay(NO_POSTS_TIME).hide SHOW_TIME, ->
				$blankPost.remove()
				postReplyClicked = no
			return

		id = postReplyBoxAppendedToId
		$.ajax
			type: "POST"
			url: "/social/api/post-post/"
			data:
				content: postContent
				replyToId: id
		.done (data) ->
			$postReplyBoxTextBox.val("")
			$postReplyBoxTextBox.text("")

			closePostReplyBox $postReplyBoxAppendedToButton
			console.log id
			if id is "NEW" or viewingSelf
				console.log "ok"
				buildPostHtml data.post, $postTopLayer, isTopLayer: yes, prepend: yes
			
			if id isnt "NEW"
				$parent = $button.parent().parent().parent().parent().parent().children(".post-replies")
				buildPostHtml data.post, $parent, prepend: yes
				$button.parent().parent().parent().parent().children(".post-footer").children(".post-view-reply").text("Close")
			postReplyClicked = no

	$postReplyBoxPost.click onPostReplyClicked




	hideChildren = ($container, func) ->
		$postReplies = $container.children ".post-replies"
		$postReplies.slideUp SHOW_TIME, ->
			$postReplies.children().remove()
			$postReplies.slideDown()
			func()



	onViewRepliesClicked = ->
		return if viewRepliesPressed
		viewRepliesPressed = yes

		$button = $(this)
		$postReplyContainer = $button.parent().parent().parent().children(".post-replies")

		if $postReplyContainer.children().length is 0
			id = $button.parent().parent().data("post-id")

			$.getJSON "/social/api/get-replies-to/#{id}/", (data) ->
				if data.posts.length is 0
					$noPosts = $ "<span>"
					$noPosts.addClass "post-small-text-left"
					$noPosts.text "No posts to display"
					$noPosts.hide()
					$button.after $noPosts
					$noPosts.show(SHOW_TIME).delay(NO_POSTS_TIME).hide SHOW_TIME, ->
						$noPosts.remove()
						viewRepliesPressed = no
				else
					for post in data.posts
						buildPostHtml post, $postReplyContainer
					$button.text "Close"
					viewRepliesPressed = no

		else
			hideChildren $postReplyContainer.parent(), ->
				$button.text "View replies"
				viewRepliesPressed = no



	onViewConversationClicked = ->
		$button = $(this)
		showNextConversationLayer = ->
			$post = $button.parent().parent()
			id = $post.data "post-is-reply-to-id"

			if not id? or id is ""
				return

			$container = $post.parent()	
			$replies = $container.children ".post-replies"

			$.getJSON "/social/api/get-post/#{id}/", (data) ->
				$post.detach()
				$replies.detach()

				buildPostHtml data.post, $container, attachToParent: yes, animate: no, showViewConversation: yes

				$container.children(".post").hide().slideDown(SHOW_TIME)
				$container.children(".post").children(".post-footer").children(".post-view-reply").text("Close")

				$postContainer = $ "<div>"
				$postContainer.addClass "post-container"
				$postContainer.append $post
				$postContainer.append $replies
				$postContainer.appendTo($container.children(".post-replies"))
				
				if data.post.isReplyTo
					$button.remove()
				else
					$button.hide(SHOW_TIME).remove()

				if data.post.isReplyTo
					$button = $container.children(".post").children(".post-header").children(".post-view-conversation")
					setTimeout showNextConversationLayer, SHOW_TIME + 100

		showNextConversationLayer()



	onDeleteClicked = ->
		$button = $(this)
		$post = $button.parent().parent()
		id = $post.data("post-id")

		new ConfirmDialogue
			title: "Deleting Post"
			body: [
				"Are you sure you want to delete this post?",
				$post.children(".post-content").text()
			]
			yesFunction: (dialogue) ->
				dialogue.close()
				$.ajax
					type: "POST"
					url: "/social/api/delete-post/"
					data:
						id: id
				.done ->
					$postTopLayer.find(".post").each ->
						foundId = $(this).data("post-id")
						if foundId is id
							$container = $(this).parent()
							$container.slideUp SHOW_TIME, ->
								$replies = $container.parent()
								$container.remove()
								if $replies.hasClass("post-replies") and $replies.children().length is 0
									$replies.parent().children(".post").children(".post-footer").children(".post-view-reply").text("View replies")

					for i in [0...topLayerVisiblePosts.length]
						if topLayerVisiblePosts[i] is id
							topLayerVisiblePosts.splice i, 1



	buildPostHtml = (post, $parent, options = { }) ->
		isTopLayer = options.isTopLayer or no
		attachToParent = options.attachToParent or no
		animate = options.animate or yes
		prepend = options.prepend or no
		showViewConversation = options.showViewConversation or no

		return if isTopLayer and isTopLayerVisiblePost post.id

		$postContainer = null
		if attachToParent
			$postContainer = $parent
		else
			$postContainer = $ "<div>"
			$postContainer.addClass "post-container"

		$post = $ "<div>"
		$post.addClass "post"

		$postHeader = $ "<header>"
		$postHeader.addClass "post-header"

		$posterLink = $ "<a>"
		$posterLink.addClass "post-poster-link"
		$posterLink.attr "href", post.poster.absoluteUrl
		$posterLink.text "#{post.poster.fullName} - @#{post.poster.username}"
		$postHeader.append $posterLink

		if post.isReplyTo and showViewConversation
			firstPost = post.isReplyTo
			$viewConversation = $ "<div>"
			$viewConversation.addClass "post-view-conversation"
			$viewConversation.text "View conversation"
			$viewConversation.click onViewConversationClicked
			$post.data "post-is-reply-to-id", firstPost.id
			$postHeader.append $viewConversation

		$postDate = $ "<div>"
		$postDate.addClass "post-date"
		$postDate.text "#{post.date}"
		$postHeader.append $postDate

		$post.append $postHeader

		$postContent = $ "<section>"
		$postContent.addClass "post-content"

		if post.isReplyTo
			firstPost = post.isReplyTo
			$firstPostUserLink = $ "<a>"
			$firstPostUserLink.addClass "post-reply-to-username"
			$firstPostUserLink.attr "href", firstPost.poster.absoluteUrl
			$firstPostUserLink.text "@#{firstPost.poster.fullName}"
			$postContent.append $firstPostUserLink
			$postContent.append ": "

		$postContent.append "#{post.content}"
		$post.append $postContent

		$postFooter = $ "<footer>"
		$postFooter.addClass "post-footer"

		$postViewReplies = $ "<div>"
		$postViewReplies.addClass "post-view-reply"
		$postViewReplies.text "View replies"
		$postFooter.append $postViewReplies

		$postPostReply = $ "<div>"
		$postPostReply.addClass "post-post-reply"
		$postPostReply.text "Post reply"
		$postFooter.append $postPostReply
		$postPostReply.click onPostReplyOpenClicked

		if post.isDeletableByLoggedInUser
			$postDelete = $ "<div>"
			$postDelete.addClass "post-delete"
			$postDelete.text "Delete"
			$postFooter.append $postDelete
			$postDelete.click onDeleteClicked


		$post.append $postFooter

		$post.data "post-id", post.id
		if isTopLayer
			topLayerVisiblePosts.push post.id

		$postContainer.prepend $post

		unless $postContainer.has(".post-replies").length
			$postReplies = $ "<div>"
			$postReplies.addClass "post-replies"
			$postContainer.append $postReplies

		if prepend
			$parent.prepend $postContainer
		else
			$parent.append $postContainer

		if animate
			$postContainer.hide 0, -> $postContainer.slideDown SHOW_TIME

		$postViewReplies.click onViewRepliesClicked




	getTopPostsApi = ""


	renderFirstPosts = (data, prepend = no) ->
		for post in data.posts
			unless isTopLayerVisiblePost(post.id)
				gotAmount += 1
				buildPostHtml post, $postTopLayer, isTopLayer: yes, prepend: prepend, showViewConversation: yes
		null



	getTopPostsApi = if viewingSelf
		"/social/api/get-posts-by-users-followed-by/#{loggedInUsername}/"
		
	else
		"/social/api/get-posts-by/#{viewingUsername}/"

	getTopPostsApi += "#{GET_POSTS_LENGTH}/"


	$.getJSON getTopPostsApi, (data) -> renderFirstPosts data

	$("#post-new-post-button").click onPostReplyOpenClicked



	loadingNext = no
	loadNextPosts = ->
		return if loadingNext
		loadingNext = yes

		getApi = getTopPostsApi + (if gotAmount is 0 then "0" else gotAmount.toString()) + "/"

		$.getJSON getApi, (data) ->
			renderFirstPosts data
			loadingNext = no
		



	$window = $(window)

	detectScroll = ->
		if $window.scrollTop() + $window.height() >= $(document).height() - WINDOW_BOTTOM_LOAD_NEW_POSTS_SCROLL
			loadNextPosts()
	
	$window.scroll detectScroll



	setInterval ->
		$.getJSON getTopPostsApi, (data) ->
			renderFirstPosts(data, yes)
	, UPDATE_TIME_SECONDS * 1000