var spiffControllers = angular.module('spiffControllers', ['restangular', 'spiffApp', 'spiff']);

spiffControllers.controller('SpiffCtrl', function($scope, Spiff) {
  $scope.space = Spiff.spaceAPI;
  $scope.user = Spiff.currentUser.$object;
});

spiffControllers.controller('DashboardCtrl', function($scope, Restangular, Spiff) {
  Spiff.currentUser.then(function(user) {
    $scope.user = user;
    $scope.invoices = [];
    _.each(user.invoices, function(invoice) {
      $scope.invoices.push(Restangular.oneUrl('invoice', invoice).get().$object);
    });
  });
});

spiffControllers.controller('InvoiceCtrl', function($scope, Restangular, $routeParams) {
  $scope.invoice = Restangular.one('invoice', $routeParams.invoiceID).get().$object;
  $scope.showPayDialog = function() {
    $('#payInvoiceModal').modal('show');
  };

  $scope.closePayDialog = function() {
    $('#payInvoiceModal').modal('hide');
  };

  $scope.processCard = function() {
    $('#payInvoiceModal :input').attr('disabled', true);
    var card = $('#card_num').val();
    var cvc = $('#cvc').val();
    var month = $('#exp_month').val();
    var year = $('#exp_year').val();
    Restangular.all('payment').post({
      invoice: '/v1/invoice/'+$routeParams.invoiceID+'/',
      value: $('#inputPayment').val(),
      stripe: {
        card: card,
        cvc: cvc,
        exp_month: month,
        exp_year: year
      }
    }).then(function(payment) {
      $scope.invoice = Restangular.one('invoice', $routeParams.invoiceID).get().$object;
      $('#payInvoiceModal').modal('hide');
      $('#payInvoiceModal').reset();
    }).finally(function() {
      console.log('fin');
      $('#payInvoiceModal :input').attr('disabled', false);
    });
  };
});
