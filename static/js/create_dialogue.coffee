window.createDialogue = (options) ->
	return null if $("body").find(".dialogue").length isnt 0

	title = options.title or ""
	body = options.body or options.content or ""
	closeButton = if options.closeButton? then options.closeButton else yes

	$dialogue = $ "<div>"
	$dialogue.addClass "dialogue"

	$dialogueVerticalCenterContainer = $ "<div>"
	$dialogueVerticalCenterContainer.addClass "dialogue-vertical-center-container"
	$dialogue.append $dialogueVerticalCenterContainer

	$dialogueContainer = $ "<div>"
	$dialogueContainer.addClass "dialogue-container"
	$dialogueVerticalCenterContainer.append $dialogueContainer

	$dialogueContainer.click -> return no

	$dialogueHeader = $ "<header>"
	$dialogueHeader.addClass "dialogue-header"

	if closeButton
		$dialogueCloseButton = $ "<div>"
		$dialogueCloseButton.addClass "dialogue-close-button"
		$dialogueCloseButton.text "X"
		$dialogueHeader.append $dialogueCloseButton
		$dialogueCloseButton.click ->
			$dialogue.remove()

		$dialogue.click ->
			$dialogue.remove()
			
	$dialogueTitle = $ "<h1>"
	$dialogueTitle.text title
	$dialogueHeader.append $dialogueTitle

	$dialogueContainer.append $dialogueHeader

	$dialogueContent = $ "<div>"
	$dialogueContent.addClass "dialogue-content"

	$dialogueContentBody = $ "<p>"
	$dialogueContentBody.text body
	$dialogueContent.append $dialogueContentBody

	$dialogueContainer.append $dialogueContent

	$("body").append($dialogue)

	return $dialogueContent



window.createConfirmDialogue = (options) ->
	options.closeButton = no
	$dialogueContent = createDialogue options
	return unless $dialogueContent?

	yesFunc = options.yesFunc or options.yesFunction or options.yes or -> yes
	noFunc = options.noFunc or options.noFunction or options.no or -> yes

	$dialogue = $dialogueContent.parent().parent().parent()

	$dialogueButtonContainer = $ "<div>"
	$dialogueButtonContainer.addClass "dialogue-button-container"

	$noButton = $ "<div>"
	$noButton.addClass "dialogue-button"
	$noButton.text "No"
	$dialogueButtonContainer.append $noButton

	$yesButton = $ "<div>"
	$yesButton.addClass "dialogue-button"
	$yesButton.text "Yes"
	$dialogueButtonContainer.append $yesButton

	handleConfirmationButtonClick = (func) -> $dialogue.remove() if func()

	$noButton.click -> handleConfirmationButtonClick noFunc
	$yesButton.click -> handleConfirmationButtonClick yesFunc
	
	$dialogueContent.append $dialogueButtonContainer