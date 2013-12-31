var spiffControllers = angular.module('spiffControllers', ['restangular', 'spiffApp', 'spiff']);

spiffControllers.controller('EpicenterCtrl', function($scope, Spiff) {
  $scope.showLogin = function() {
    $('#loginModal').modal('show');
  };

  $scope.hideLogin = function() {
    $('#loginModal').modal('hide');
  };

  $scope.login = function() {
    var username = $('#username').val();
    var password = $('#password').val();
    Spiff.login(username, password).then(function() {
      $scope.hideLogin()
    });
  };

  $scope.logout = function() {
    Spiff.logout();
  };

  $scope.$on('loginRequired', function() {
    $scope.showLogin();
  });
});

spiffControllers.controller('DashboardCtrl', function($scope, Restangular, Spiff, $location) {
  $scope.$watch('Spiff.currentUser', function(user) {
    if (user != null) {
      $scope.user = user;
      $scope.invoices = [];
      _.each(user.invoices, function(invoice) {
        $scope.invoices.push(Restangular.oneUrl('invoice', invoice).get().$object);
      });
    } else {
      $location.url("/welcome");
    }
  });
});

spiffControllers.controller('AnonDashCtrl', function($scope, $rootScope, $scope, Spiff, $location) {
  $scope.showLogin = function() {
    $rootScope.$broadcast('loginRequired');
  }

  $scope.$watch('Spiff.currentUser', function(user) {
    if (user != null) {
      $location.url('/');
    }
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
      $('#payInvoiceModal :input').attr('disabled', false);
    });
  };
});
