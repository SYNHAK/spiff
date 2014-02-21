var Spiff = angular.module('spiff', [
  'restangular',
  'spaceapi'
]);

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

Spiff.factory('SpiffRestangular', function(SpiffConfig, Restangular) {
  return Restangular.withConfig(function(RestangularConfigurer) {
    RestangularConfigurer.setBaseUrl(SpiffConfig.baseUrl);
    RestangularConfigurer.setParentless(false);
    RestangularConfigurer.setRequestSuffix('/');
    RestangularConfigurer.setDefaultHttpFields({withCredentials: true});
    RestangularConfigurer.setErrorInterceptor(function(response) {
      var $injector = angular.element('body').injector();
      if (response.status == 401) {
        $injector.get('$rootScope').$broadcast('loginRequired');
      } else {
        console.log(response);
        $injector.get('$modal').open({
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
      }
      return true;
    });

    RestangularConfigurer.addElementTransformer('member', true, function(member) {
      if (member.addRestangularMethod) {
        member.addRestangularMethod('login', 'post', 'login');
        member.addRestangularMethod('logout', 'get', 'logout');
        member.addRestangularMethod('search', 'get', 'search');
      }
      return member;
    });

    RestangularConfigurer.addElementTransformer('member', false, function(member) {
      if (member.addRestangularMethod) {
        member.addRestangularMethod('getStripeCards', 'get', 'stripeCards');
        member.addRestangularMethod('addStripeCard', 'post', 'stripeCards');
        member.addRestangularMethod('removeStripeCard', 'remove', 'stripeCards');
      }
      return member;
    });

    RestangularConfigurer.setResponseExtractor(function(response, operation, what, url) {
      var newResponse;
      if (operation == 'getList') {
        newResponse = response.objects;
        newResponse.meta = response.meta;
      } else {
        newResponse = response;
      }
      return newResponse;
    });

  });
});

Spiff.provider('SpiffConfig', function() {
  var baseUrl = null;
  this.setBaseUrl = function(url) {
    baseUrl = url;
  }

  this.$get = function() {
    return {
      baseUrl: baseUrl
    }
  };
});

Spiff.provider('Spiff', function() {

  this.$get = function(SpaceAPI, SpiffRestangular, $q, $rootScope, $http) {
    var scope = $rootScope.$new();

    scope.refreshUser = function() {
      return SpiffRestangular.one('member', 'self').get().then(function(user) {
        scope.currentUser = user;
      });
    }

    scope.login = function(username, password) {
      if (password === undefined) {
        return scope.refreshUser();
      } else {
        return SpiffRestangular.all('member').login({
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
      return SpiffRestangular.all('member').logout().then(function() {
        console.log('logged out');
        scope.refreshUser();
      });
    };
    scope.currentUser = null;

    scope.checkPermission = function(perm) {
      var member = SpiffRestangular.one('member', 'self');
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
