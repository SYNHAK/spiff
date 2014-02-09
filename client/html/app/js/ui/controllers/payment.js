angular.module('spiff.payment', [
  'spiff',
  'restangular',
])

.controller('PayInvoiceCtrl', function($scope, $modalInstance, Restangular, invoice) {
  console.log(invoice);

  $scope.d = {};
  $scope.d.value = invoice.unpaidBalance;

  $scope.process = function() {
    $('#payInvoiceModal :input').attr('disabled', true);
    var card = $scope.d.card_num;
    var cvc = $scope.d.cvc;
    var month = $scope.d.month;
    var year = $scope.d.year;
    Restangular.all('payment').post({
      invoice: '/v1/invoice/'+invoice.id+'/',
      value: $scope.d.value,
      stripe: {
        card: card,
        cvc: cvc,
        exp_month: month,
        exp_year: year
      }
    }).then(function(payment) {
      $modalInstance.close();
    });
  }

  $scope.close = function() {
    $modalInstance.close();
  }
})

.controller('InvoiceCtrl', function($scope, Restangular, $stateParams, $modal) {
  var invoice = Restangular.one('invoice', $stateParams.invoiceID);

  $scope.refresh = function() {
    invoice.get().then(function (i) {
      $scope.invoice = i;
    });
  }

  $scope.payInvoice = function() {
    var modal = $modal.open({
      templateUrl: 'invoices/modal/pay.html',
      controller: 'PayInvoiceCtrl',
      resolve: {invoice: function() {return $scope.invoice}}
    });
    modal.result.then(function() {
      $scope.refresh();
    });
  };

  $scope.refresh();
});
