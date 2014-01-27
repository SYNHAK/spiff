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

Spiff.directive('checkPermission', function(Spiff, $rootScope) {
  return {
    link: function(scope, element, attrs) {
      scope.$watch('Spiff.currentUser', function(user) {
        if (attrs.checkPermission != undefined) {
          Spiff.checkPermission(scope.$eval(attrs.checkPermission)).then(function (result) {
            scope.hasPermission = result;
          });
        } else {
          scope.hasPermission = false;
        }
      });
    },
  };
});

Spiff.provider('Spiff', function(RestangularProvider) {
  var baseURL = null;
  this.setBaseURL = function(url) {
    baseURL = url;
  }

  RestangularProvider.addElementTransformer('group', false, function(group) {
    group.addRestangularMethod('getMembers', 'get', 'members');
    return group;
  });

  RestangularProvider.addElementTransformer('member', true, function(member) {
    member.addRestangularMethod('login', 'post', 'login');
    member.addRestangularMethod('logout', 'get', 'logout');
    member.addRestangularMethod('search', 'get', 'search');
    return member;
  });

  RestangularProvider.addElementTransformer('member', false, function(member) {
    member.addRestangularMethod('getStripeCards', 'get', 'stripeCards');
    member.addRestangularMethod('addStripeCard', 'post', 'stripeCards');
    member.addRestangularMethod('removeStripeCard', 'remove', 'stripeCards');
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
          return user;
        }, function(reason) {
          scope.$broadcast('loginFailed');
          return reason;
        });
      }
    };

    scope.logout = function() {
      return Restangular.all('member').logout().then(function() {
        console.log('logged out');
        scope.refreshUser();
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
