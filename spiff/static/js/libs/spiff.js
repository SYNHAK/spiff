var Spiff = angular.module('spiff', [
  'restangular'
]);

Spiff.provider('SpaceAPI', function() {
  var baseURL = '/';
  this.setBaseURL = function(url) {
    baseURL = url;
  }

  this.$get = function($http) {
    return {
      update: function() {
        return $http.get(baseURL);
      }
    };
  }
});

Spiff.controller('SpiffAuthCtrl', function($scope, Spiff) {
  $scope.user = Spiff.currentUser;
});

Spiff.provider('Spiff', function(RestangularProvider) {
  var baseURL = null;
  this.setBaseURL = function(url) {
    baseURL = url;
  }
  RestangularProvider.addElementTransformer('member', true, function(member) {
    member.addRestangularMethod('login', 'post', 'login');
    member.addRestangularMethod('logout', 'get', 'logout');
    member.addRestangularMethod('search', 'get', 'search');
    return member;
  });

  RestangularProvider.setResponseExtractor(function(response, operation, what, url) {
    var newResponse;
    if (operation == 'getList') {
      newResponse = response.objects;
      newResponse.meta = response.meta;
    } else {
      newResponse = response;
    }
    return newResponse;
  });

  this.$get = function(Restangular, $q, $rootScope) {
    var scope = $rootScope.$new();
    $rootScope.Spiff = scope;

    scope.login = function(username, password) {
      if (password === undefined) {
        return Restangular.one('member', 'self').get().then(function(user) {
          scope.currentUser = user;
        }, function(reason) {
          scope.currentUser = null;
        });
      }
      return Restangular.all('member').login({
        username: username,
        password: password
      }).then(function(user) {
        Restangular.one('member', 'self').get().then(function(user) {
          scope.currentUser = user;
        });
      });
    };

    scope.logout = function() {
      return Restangular.all('member').logout().then(function() {
        console.log('logged out');
        scope.currentUser = null;
      });
    };
    scope.currentUser = null;

    return scope;
  }
});
