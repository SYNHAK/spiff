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
  $scope.checkPermission = Spiff.checkPermission;
});

Spiff.directive('checkPermission', function(Spiff, $rootScope) {
  return {
    link: function(scope, element, attrs) {
      scope.$watch('Spiff.currentUser', function(user) {
        Spiff.checkPermission(attrs.if_has_permission).then(function (result) {
          scope.hasPermission = result;
        });
      });
    },
  };
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

  this.$get = function(Restangular, $q, $rootScope, $http) {
    var scope = $rootScope.$new();
    $rootScope.Spiff = scope;

    scope.refreshUser = function() {
      return Restangular.one('member', 'self').get().then(function(user) {
        scope.currentUser = user;
      });
    }

    scope.login = function(username, password) {
      if (password === undefined) {
        return scope.refreshUser();
      } else {
        return Restangular.all('member').login({
          username: username,
          password: password
        }).then(function(user) {
          scope.refreshUser();
        });
      }
    };

    scope.logout = function() {
      return Restangular.all('member').logout().then(function() {
        console.log('logged out');
        scope.currentUser = null;
      });
    };
    scope.currentUser = null;

    scope.checkPermission = function(perm) {
      var member = Restangular.one('member', 'self');
      var ret = $q.defer();
      $http.get(member.getRestangularUrl()+'/has_permission/'+perm).success(function() {
        ret.resolve(true);
      }).error(function() {
        ret.resolve(false);
      });
      return ret.promise;
    }

    return scope;
  }
});
