var spiffApp = angular.module('spiffApp', [
  'restangular',
  'spiffControllers',
  'spiffDirectives',
  'spiff',
  'ngRoute',
  'ui-gravatar',
  'md5'
]);

spiffApp.config(function($routeProvider, RestangularProvider, SpiffProvider) {
  $routeProvider.
    when('/', {
      templateUrl: 'dashboard/index.html',
      controller: 'DashboardCtrl'
    }).
    when('/welcome', {
      templateUrl: 'dashboard/index-anonymous.html',
      controller: 'AnonDashCtrl'
    }).
    when('/invoices/:invoiceID', {
      templateUrl: 'invoices/detail.html',
      controller: 'InvoiceCtrl'
    }).
    when('/resources', {
      templateUrl: 'resources/index.html',
      controller: 'ResourceListCtrl'
    }).
    when('/resources/:resourceID', {
      templateUrl: 'resources/detail.html',
      controller: 'ResourceCtrl'
    }).
    when('/members', {
      templateUrl: 'members/index.html',
      controller: 'MemberListCtrl'
    }).
    when('/members/:memberID', {
      templateUrl: 'members/detail.html',
      controller: 'MemberCtrl'
    }).
    when('/sensors', {
      templateUrl: 'sensors/index.html',
      controller: 'SensorListCtrl',
    }).
    when('/sensors/:sensorID', {
      templateUrl: 'sensors/detail.html',
      controller: 'SensorCtrl',
    }).
    when('/donate', {
      templateUrl: 'donate/index.html',
      controller: 'DonateCtrl',
    }).
    otherwise({
      redirectTo: '/'
    });

  RestangularProvider.setBaseUrl('../v1');
  RestangularProvider.setParentless(false);
  RestangularProvider.setRequestSuffix('\\');
  RestangularProvider.setErrorInterceptor(function(response) {
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

  SpiffProvider.setBaseURL('../');
});

spiffApp.run(function(Spiff) {
  Spiff.login();
});
