// Generated by CoffeeScript 1.4.0
(function() {

  $(document).ready(function() {
    var $cancelButtons, $loginButton, $loginForm, $registerButton, $registerForm, $title, $titleText, FormState, animateInForm, animateOutForm, animateTime, fontSizeLarge, fontSizeSmall, halfTitleHeightLarge, reopenDelay, showingFormState, titleHeightLarge, titleHeightSmall;
    $title = $("#index-title");
    $titleText = $title.children("h1");
    $registerForm = $("#register-form");
    $registerButton = $("#register-button");
    $loginForm = $("#login-form");
    $loginButton = $("#login-button");
    $cancelButtons = $(".index-form-cancel-button");
    titleHeightLarge = "480px";
    halfTitleHeightLarge = "240px";
    titleHeightSmall = "38px";
    fontSizeLarge = "6em";
    fontSizeSmall = "1.4em";
    animateTime = 280;
    reopenDelay = 100;
    FormState = {
      NO_FORM: 0,
      REGISTER: 1,
      LOGIN: 2,
      ANIMATING: 3
    };
    showingFormState = FormState.NO_FORM;
    animateInForm = function($form, formState, instant) {
      var time;
      if (showingFormState === FormState.NO_FORM) {
        showingFormState = FormState.ANIMATING;
        time = instant ? 1 : animateTime;
        $form.removeClass("invisible");
        $title.animate({
          height: titleHeightSmall,
          "line-height": titleHeightSmall
        }, time, function() {
          return showingFormState = formState;
        });
        return $titleText.animate({
          "font-size": fontSizeSmall
        }, time);
      } else if (showingFormState === formState) {
        return animateOutForm();
      } else if (showingFormState !== FormState.ANIMATING) {
        animateOutForm();
        return setTimeout(function() {
          return animateInForm($form, formState);
        }, animateTime + reopenDelay);
      }
    };
    animateOutForm = function() {
      if (showingFormState === FormState.NO_FORM || showingFormState === FormState.ANIMATING) {
        return;
      }
      showingFormState = FormState.ANIMATING;
      $title.animate({
        height: titleHeightLarge,
        "line-height": halfTitleHeightLarge
      }, animateTime, function() {
        $registerForm.addClass("invisible");
        $loginForm.addClass("invisible");
        return showingFormState = FormState.NO_FORM;
      });
      return $titleText.animate({
        "font-size": fontSizeLarge
      }, animateTime);
    };
    $registerButton.click(function() {
      return animateInForm($registerForm, FormState.REGISTER);
    });
    $loginButton.click(function() {
      return animateInForm($loginForm, FormState.LOGIN);
    });
    $cancelButtons.click(function() {
      return animateOutForm();
    });
    if (typeof autoOpenTo !== "undefined" && autoOpenTo !== null) {
      if (autoOpenTo === "register") {
        return animateInForm($registerForm, FormState.REGISTER, true);
      } else if (autoOpenTo === "login") {
        return animateInForm($loginForm, FormState.LOGIN, true);
      }
    }
  });

}).call(this);
