var spiffApp = angular.module('spiffApp', [
  'restangular',
  'spiffDirectives',
  'spiff',
  'spiff.dashboard',
  'spiff.epicenter',
  'spiff.members',
  'spiff.resources',
  'spiff.donate',
  'spiff.sensors',
  'spiff.payment',
  'ngRoute',
  'ui-gravatar',
  'md5',
  'ui.bootstrap.modal',
  'ui.router',
  'template/modal/window.html',
  'template/modal/backdrop.html'
]);

spiffApp.config(function($stateProvider, $urlRouterProvider, RestangularProvider, SpiffProvider) {
  $urlRouterProvider.otherwise('/');
  $stateProvider
    .state('dashboard', {
      url: '/',
      templateUrl: 'dashboard/index.html',
      controller: 'DashboardCtrl',
    })
    .state('welcome', {
      url: '/welcome',
      templateUrl: 'dashboard/index-anonymous.html',
      controller: 'AnonDashCtrl'
    })
    .state('viewInvoice', {
      url: '/invoices/:invoiceID',
      templateUrl: 'invoices/detail.html',
      controller: 'InvoiceCtrl'
    })
    .state('listResources', {
      url: '/resources',
      templateUrl: 'resources/index.html',
      controller: 'ResourceListCtrl'
    })
    .state('viewResource', {
      url: '/resources/:resourceID',
      templateUrl: 'resources/detail.html',
      controller: 'ResourceCtrl',
    })
    .state('listMembers', {
      url: '/members',
      templateUrl: 'members/index.html',
      controller: 'MemberListCtrl',
    })
    .state('member', {
      url: '/members/:memberID',
      templateUrl: 'members/detail.html',
      controller: 'MemberViewCtrl'
    })
    .state('member.view', {
      url: '',
      templateUrl: 'members/view.html',
      controller: 'MemberViewCtrl',
    })
    .state('member.subscriptions', {
      url: '/subscriptions',
      templateUrl: 'members/subscriptions.html',
      controller: 'SubscriptionCtrl',
    })
    .state('member.edit', {
      url: '/edit',
      templateUrl: 'members/edit.html',
      controller: 'EditMemberCtrl'
    })
    .state('member.payments', {
      url: '/payment',
      templateUrl: 'members/payment.html',
      controller: 'MemberPaymentCtrl'
    })
    .state('listSensors', {
      url: '/sensors',
      templateUrl: 'sensors/index.html',
      controller: 'SensorListCtrl',
    })
    .state('viewSensor', {
      url: '/sensors/:sensorID',
      templateUrl: 'sensors/detail.html',
      controller: 'SensorCtrl'
    })
    .state('donate', {
      url: '/donate',
      templateUrl: 'donate/index.html',
      controller: 'DonateCtrl',
    })
    .state('register', {
      url: '/register',
      templateUrl: 'register.html',
      controller: 'RegistrationCtrl'
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
