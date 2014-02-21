angular.module('spiff.epicenter', [
  'spiff',
  'spaceapi'
])

.controller('LoginCtrl', function($scope, $modalInstance, Spiff) {
  $scope.d = {};

  $scope.login = function() {
    var username = $scope.d.username;
    var password = $scope.d.password;
    Spiff.login(username, password).then(function(user) {
      if (user.status >= 300 || user.status < 200) {
        if (user.status == 401) {
          $scope.error = "Incorrect username or password";
          $('#loginModal #error-msg').text("Incorrect username or password");
        }
      } else {
        $scope.error = null;
        $modalInstance.close()
      }
    });
  };

  $scope.cancel = function() {
    $modalInstance.dismiss();
  }
})

.controller('EpicenterCtrl', function($scope, Spiff, $modal, SpaceAPI) {
  $scope.Spiff = Spiff;

  $scope.showLogin = function() {
    $modal.open({
      templateUrl: 'partials/login.html',
      controller: 'LoginCtrl'
    });
  };

  $scope.enterAdmin = function() {
    $modal.open({
      templateUrl: 'partials/open-admin.html',
      controller: function($scope, $modalInstance) {
        $scope.close = function() {$modalInstance.close();}
      }
    });
  };

  $scope.logout = function() {
    Spiff.logout();
  };

  Spiff.$on('loginRequired', function() {
    $scope.showLogin();
  });

  SpaceAPI.ready(function(api) {
    $scope.spaceAPI = api;
  });
});
