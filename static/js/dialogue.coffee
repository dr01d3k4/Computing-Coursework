class Dialogue
	constructor: (options) ->
		return null if $("body").find(".dialogue").length isnt 0

		@title = options.title or ""
		@body = options.body or options.content or [ ]
		@hasCloseButton = if options.closeButton? then options.closeButton else if options.hasCloseButton? then	options.hasCloseButton else yes

		@$dialogue = $ "<div>"
		@$dialogue.addClass "dialogue"

		@$dialogueVerticalCenterContainer = $ "<div>"
		@$dialogueVerticalCenterContainer.addClass "dialogue-vertical-center-container"
		@$dialogue.append @$dialogueVerticalCenterContainer

		@$dialogueContainer = $ "<div>"
		@$dialogueContainer.addClass "dialogue-container"
		@$dialogueVerticalCenterContainer.append @$dialogueContainer
		@$dialogueContainer.click -> return no

		@width = options.width or @$dialogueContainer.css "max-width"
		@$dialogueContainer.css "max-width", @width

		@$dialogueHeader = $ "<header>"
		@$dialogueHeader.addClass "dialogue-header"

		if @hasCloseButton
			@$dialogueCloseButton = $ "<div>"
			@$dialogueCloseButton.addClass "dialogue-close-button"
			@$dialogueCloseButton.text "X"
			@$dialogueHeader.append @$dialogueCloseButton
			@$dialogueCloseButton.click =>
				@onCloseButtonClicked()
				
			@$dialogue.click =>
				@onCloseButtonClicked
				
		@$dialogueTitle = $ "<h1>"
		@$dialogueTitle.text @title
		@$dialogueHeader.append @$dialogueTitle

		@$dialogueContainer.append @$dialogueHeader

		@$dialogueContent = $ "<div>"
		@$dialogueContent.addClass "dialogue-content"

		for body in @body
			@$dialogueContentBody = $ "<p>"
			@$dialogueContentBody.text body
			@$dialogueContent.append @$dialogueContentBody

		@$dialogueContainer.append @$dialogueContent

		@$dialogue.appendTo $("body")



	close: ->
		@$dialogue.remove() if @$dialogue?



	onCloseButtonClicked: ->
		@close()



class ConfirmDialogue extends Dialogue
	constructor: (options) ->
		options.closeButton = no
		options.hasCloseButton = no
		super options
		return unless @$dialogue?

		@yesFunction = options.yesFunc or options.yesFunction or options.yes or -> yes

		@noFunction = options.noFunc or options.noFunction or options.no or -> yes

		@$dialogueButtonContainer = $ "<div>"
		@$dialogueButtonContainer.addClass "dialogue-button-container"

		@$noButton = $ "<div>"
		@$noButton.addClass "dialogue-button"
		@$noButton.text "No"
		@$dialogueButtonContainer.append @$noButton

		@$yesButton = $ "<div>"
		@$yesButton.addClass "dialogue-button"
		@$yesButton.text "Yes"
		@$dialogueButtonContainer.append @$yesButton

		@$noButton.click =>
			@handleConfirmationButtonClick @noFunction

		@$yesButton.click =>
			@handleConfirmationButtonClick @yesFunction
		
		@$dialogueContent.append @$dialogueButtonContainer



	onCloseButtonClicked: ->
		throw "Confirm dialogue doesn't have a close button"



	handleConfirmationButtonClick: (buttonClickedFunction) ->
		@close() if buttonClickedFunction @



window.Dialogue = Dialogue
window.ConfirmDialogue = ConfirmDialogue