$(document).ready ->
	$postTopLayer = $ "#post-top-layer"


	showSpeed = 250
	noPostsTime = 600
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
		$postReplyBox.slideUp showSpeed, -> $postReplyBox.detach()
		$button.text "Post reply"

		$postReplyBoxAppendedToButton = null
		postReplyBoxAppendedToId = -1



	onPostReplyOpenClicked = ->
		$button = $(this)
		id = $button.parent().parent().children(".post-id-meta").text()

		if $postReplyBoxAppendedToButton?.is $button
			closePostReplyBox $button

		else
			if $postReplyBoxAppendedToButton?
			 	$postReplyBoxAppendedToButton.text "Post reply"

			$button.text "Close"

			$postReplyBoxAppendedToButton = $button
			postReplyBoxAppendedToId = id

			$postReplyBox.slideUp showSpeed, ->
				$postReplyBox.appendTo($button.parent().parent()).hide().slideDown showSpeed, ->
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
			$blankPost.show(showSpeed).delay(noPostsTime).hide showSpeed, ->
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
			$postReplyBoxTextBox.val("");
			$postReplyBoxTextBox.text("");

			closePostReplyBox $postReplyBoxAppendedToButton
			if id is "NEW" or viewingSelf
				buildPostHtml data.post, $postTopLayer, yes, no, yes, yes
			
			if id isnt "NEW"
				$parent = $button.parent().parent().parent().parent().parent().children(".post-replies");
				buildPostHtml data.post, $parent, no, no, yes, yes
				$button.parent().parent().parent().parent().children(".post-footer").children(".post-view-reply").text("Close")
			postReplyClicked = no

	$postReplyBoxPost.click onPostReplyClicked




	hideChildren = ($container, func) ->
		$postReplies = $container.children ".post-replies"
		$postReplies.slideUp showSpeed, ->
			$postReplies.children().remove()
			$postReplies.slideDown()
			func()



	onViewRepliesClicked = ->
		return if viewRepliesPressed
		viewRepliesPressed = yes

		$button = $(this)
		$postReplyContainer = $button.parent().parent().parent().children(".post-replies")

		if $postReplyContainer.children().length is 0
			id = $button.parent().parent().children(".post-id-meta").text()

			$.getJSON "/social/api/get-replies-to/#{id}/", (data) ->
				if data.posts.length is 0
					$noPosts = $ "<span>"
					$noPosts.addClass "post-small-text-left"
					$noPosts.text "No posts to display"
					$noPosts.hide()
					$button.after $noPosts
					$noPosts.show(showSpeed).delay(noPostsTime).hide showSpeed, ->
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
			id = $button.children(".post-is-reply-to-id").text()
			if id is ""
				return

			$post = $button.parent().parent()
			$container = $post.parent()	
			$replies = $container.children ".post-replies"

			$.getJSON "/social/api/get-post/#{id}/", (data) ->
				$post.detach()
				$replies.detach()

				buildPostHtml data.post, $container, no, yes, no, no, yes

				$container.children(".post").hide().slideDown(showSpeed)
				$container.children(".post").children(".post-footer").children(".post-view-reply").text("Close")

				$postContainer = $ "<div>"
				$postContainer.addClass "post-container"
				$postContainer.append $post
				$postContainer.append $replies
				$postContainer.appendTo($container.children(".post-replies"))
				
				if data.post.isReplyTo
					$button.remove()
				else
					$button.hide(showSpeed).remove()

				if data.post.isReplyTo
					$button = $container.children(".post").children(".post-header").children(".post-view-conversation")
					setTimeout showNextConversationLayer, showSpeed + 100

		showNextConversationLayer()



	onDeleteClicked = ->
		$button = $(this)
		$post = $button.parent().parent()
		id = $post.children(".post-id-meta").text()

		createConfirmDialogue
			title: "Delete Post"
			body: "Are you sure you want to delete this post"
			yesFunction: ->
				$.ajax
					type: "POST"
					url: "/social/api/delete-post/"
					data:
						id: id
				.done ->
					$postTopLayer.find(".post-id-meta").each ->
						$id = $(this)
						if $id.text() is id
							$container = $id.parent().parent()
							$container.slideUp showSpeed, ->
								$replies = $container.parent()
								$container.remove()
								if $replies.hasClass("post-replies") and $replies.children().length is 0
									$replies.parent().children(".post").children(".post-footer").children(".post-view-reply").text("View replies")

				return yes


	buildPostHtml = (post, $parent, isTopLayer = no, attachToParent = no, animate = yes, prepend = no, showViewConversation = no) ->
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
			$viewConversation.append "<span class='post-is-reply-to-id'>#{firstPost.id}</span>"
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

		if post.isDeletableByLoggedInUser # poster.username is loggedInUsername
			$postDelete = $ "<div>"
			$postDelete.addClass "post-delete"
			$postDelete.text "Delete"
			$postFooter.append $postDelete
			$postDelete.click onDeleteClicked


		$post.append $postFooter

		$postIdMeta = $ "<div>"
		$postIdMeta.addClass "post-id-meta"
		$postIdMeta.text post.id
		$post.append $postIdMeta

		$postContainer.prepend $post

		unless $postContainer.has(".post-replies").length
			$postReplies = $ "<div>"
			$postReplies.addClass "post-replies"
			$postContainer.append $postReplies

		if animate
			$postContainer.hide()
			if prepend
				$parent.prepend $postContainer
			else
				$parent.append $postContainer
			$postContainer.slideDown showSpeed
		else
			if prepend
				$parent.prepend $postContainer
			else
				$parent.append $postContainer

		$postViewReplies.click onViewRepliesClicked



	renderFirstPosts = (data) ->
		for post in data.posts
			buildPostHtml post, $postTopLayer, yes, no, yes, no, yes
		null



	if viewingSelf
		$.getJSON "/social/api/get-posts-by-users-followed-by/#{loggedInUsername}/", renderFirstPosts
	else
		$.getJSON "/social/api/get-posts-by/#{viewingUsername}/", renderFirstPosts

	$("#post-new-post-button").click onPostReplyOpenClicked