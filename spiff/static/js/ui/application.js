var spiffApp = angular.module('spiffApp', [
  'restangular',
  'spiffControllers',
  'ngRoute'
]);

spiffApp.config(function($routeProvider, RestangularProvider) {
  $routeProvider.
    when('/', {
      templateUrl: 'dashboard/index.html',
      controller: 'DashboardCtrl'
    }).
    when('/invoices/:invoiceID', {
      templateUrl: 'invoices/detail.html',
      controller: 'InvoiceCtrl'
    }).otherwise({
      redirectTo: '/'
    });

  RestangularProvider.setBaseUrl('../v1');
  RestangularProvider.setParentless(false);
  RestangularProvider.setRequestSuffix('\\');
  RestangularProvider.setErrorInterceptor(function(response) {
    console.log(response.data.traceback);
    $('#errorModal #message').text(response.data.error_message);
    $('#errorModal #traceback').text(response.data.traceback);
    $('#errorModal').modal('show');
    return true;
  });
});
