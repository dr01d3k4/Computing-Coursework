// Generated by CoffeeScript 1.4.0
(function() {

  $(document).ready(function() {
    var $logoutButton;
    $logoutButton = $("#logout-button");
    return $logoutButton.click(function() {
      return $.ajax({
        type: "POST",
        url: "/api/logout/"
      }).done(function(data) {
        return window.location.href = "/";
      });
    });
  });

}).call(this);
