angular.module('spiff.epicenter', [
  'spiff',
  'spaceapi',
  'messages'
])

.controller('ChangePassCtrl', function($scope, $modalInstance, Spiff, SpiffRestangular, Messages) {
  $scope.d = {};

  $scope.requestReset = function() {
    SpiffRestangular.one('member', Spiff.currentUser.id).patch({'currentPassword': $scope.d.current, 'password': $scope.d.new});
    Messages.info("Password changed.");
  }
})

.controller('ResetPassCtrl', function($scope, $modalInstance, SpiffRestangular, Messages) {
  $scope.d = {};

  $scope.requestReset = function() {
    SpiffRestangular.all('member').requestPasswordReset({'userid': $scope.d.userid}).then(function() {
      Messages.info("Password reset requested. Check your email.");
      $modalInstance.close();
    });
  };
})

.controller('LoginCtrl', function($scope, $modalInstance, Spiff) {
  $scope.d = {};

  $scope.login = function() {
    var username = $scope.d.username;
    var password = $scope.d.password;
    Spiff.login(username, password).then(function(user) {
      if (user.status >= 300 || user.status < 200) {
        if (user.status == 401) {
          $scope.error = "Incorrect username or password";
        }
      } else {
        $scope.error = null;
        $modalInstance.close()
      }
    });
  };
})

.controller('EpicenterCtrl', function($scope, Spiff, $modal, SpaceAPI) {
  $scope.Spiff = Spiff;

  var loginIsOpen = false;

  $scope.showLogin = function() {
    console.log("Login is opened: "+loginIsOpen);
    if (!loginIsOpen) {
      loginIsOpen = true;
      $modal.open({
        templateUrl: 'partials/login.html',
        controller: 'LoginCtrl'
      }).result.then(function() {
        console.log("Finished login");
        loginIsOpen = false;
      });
    }
  };

  $scope.showPasswordReset = function() {
    $modal.open({
      templateUrl: 'partials/reset-password.html',
      controller: 'ResetPassCtrl',
    }).result.then(function() {
    });
  };

  $scope.changePassword = function() {
    $modal.open({
      templateUrl: 'partials/change-password.html',
      controller: 'ChangePassCtrl',
    }).result.then(function() {
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

  $scope.$on('showLogin', function() {
    $scope.showLogin();
  });

  Spiff.$on('loginRequired', function(element, response) {
    $scope.showLogin();
  });

  Spiff.$on('error', function(element, response) {
    $modal.open({
      templateUrl: 'error.html',
      controller: function($scope, $modalInstance) {
        $scope.status = response.status;
        $scope.message = response.data.error_message;
        $scope.traceback = response.data.traceback;
        $scope.close = function() {
          $modalInstance.close();
        }
      }
    });
  });

  SpaceAPI.ready(function(api) {
    $scope.spaceAPI = api;
  });
});
