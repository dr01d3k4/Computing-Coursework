$(document).ready ->
	$title = $ "#index-title"
	$titleText = $title.children("h1")

	$registerForm = $ "#register-form"
	$registerButton = $ "#register-button"

	$loginForm = $ "#login-form"
	$loginButton = $ "#login-button"

	$cancelButtons = $ ".index-form-cancel-button"



	titleHeightLarge = "480px"
	halfTitleHeightLarge = "240px";
	titleHeightSmall = "38px"
	fontSizeLarge = "6em"
	fontSizeSmall = "1.4em"

	animateTime = 280
	reopenDelay = 100



	FormState = 
		NO_FORM: 0
		REGISTER: 1
		LOGIN: 2
		ANIMATING: 3

	showingFormState = FormState.NO_FORM



	animateInForm = ($form, formState, instant) ->
		if showingFormState is FormState.NO_FORM	
			showingFormState = FormState.ANIMATING

			time = if instant then 1 else animateTime

			$form.removeClass "invisible"
			$title.animate {
				height: titleHeightSmall,
				"line-height": titleHeightSmall,
			}, time, ->
				showingFormState = formState
			$titleText.animate {"font-size": fontSizeSmall}, time

		else if showingFormState is formState
			animateOutForm()

		else if showingFormState isnt FormState.ANIMATING
			animateOutForm()
			setTimeout ->
				animateInForm $form, formState
			, animateTime + reopenDelay


	animateOutForm = ->
		return if showingFormState is FormState.NO_FORM or showingFormState is FormState.ANIMATING
		
		showingFormState = FormState.ANIMATING

		$title.animate {
			height: titleHeightLarge,
			"line-height": halfTitleHeightLarge,
		}, animateTime, ->
			$registerForm.addClass "invisible"
			$loginForm.addClass "invisible"
			showingFormState = FormState.NO_FORM
		$titleText.animate {"font-size": fontSizeLarge}, animateTime



	$registerButton.click ->
		animateInForm $registerForm, FormState.REGISTER



	$loginButton.click ->
		animateInForm $loginForm, FormState.LOGIN



	$cancelButtons.click ->
		animateOutForm()

		

	if autoOpenTo?
		if autoOpenTo is "register"
			animateInForm $registerForm, FormState.REGISTER, yes
		else if autoOpenTo is "login"
			animateInForm $loginForm, FormState.LOGIN, yes