angular.module('spiff.dashboard', [
  'restangular',
  'spiff'
])

.controller('UnsubscribeCtrl', function($scope, $modalInstance, Restangular, subscription) {
  $scope.subscription = subscription;
  $scope.close = $modalInstance.close;
  $scope.unsubscribe = function() {
    Restangular.one('subscription', subscription.id).remove().then(function () {
      $modalInstance.close();
    });
  }
})

.controller('AddPaymentCardCtrl', function($scope, $modalInstance, user) {
  $scope.d = {};
  $scope.save = function() {
    $scope.saving = true;
    var card = $scope.d.card_num;
    var cvc = $scope.d.cvc;
    var month = $scope.d.month;
    var year = $scope.d.year;
    user.addStripeCard({
      card: card,
      cvc: cvc,
      exp_month: month,
      exp_year: year
    }).then(function(cardData) {
      $modalInstance.close();
    });
  };

  $scope.cancel = function() {$modalInstance.close()};
})

.controller('DashboardCtrl', function($scope, Restangular, Spiff, $location, $modal) {
  $scope.$watch('Spiff.currentUser', function(user) {
    if (user && !user.isAnonymous) {
      $scope.user = user;
      $scope.invoices = [];
      _.each(user.invoices, function(invoice) {
        $scope.invoices.push(Restangular.oneUrl('invoice', invoice).get().$object);
      });


      $scope.stripeCards = null;
      $scope.refreshCards = function() {
        return user.getStripeCards().then(function (cards) {
          var cardList = [];
          _.each(cards.cards, function(c) {
            cardList.push(c);
          });
          $scope.stripeCards = cardList;
        });
      }

      $scope.refreshCards();

      $scope.refreshSubscriptions = function() {
      }

      $scope.refreshSubscriptions();

      $scope.startUnsubscribe = function(subscription) {
        var modal = $modal.open({
          templateUrl: 'dashboard/modal/unsubscribe.html',
          controller: 'UnsubscribeCtrl',
          resolve: {subscription: function() {return subscription;}}
        });
        modal.result.then(function() {
          $scope.refreshSubscriptions();
        });
      }

      $scope.addPaymentCard = function() {
        var modal = $modal.open({
          templateUrl: 'dashboard/modal/add-payment-card.html',
          controller: 'AddPaymentCardCtrl',
          resolve: {user: function() {return user}}
        });
        modal.result.then(function() {
          $scope.refreshCards();
        });
      }

      $scope.removeCard = function(card) {
        user.one('stripeCards', card.id).remove().then(function() {
          $scope.refreshCards();
        });
      }

      $scope.hideUnsubscribe  = function() {
        $('#subscriptionUnsubscribeModal').modal('hide');
      }

    } else if (user && user.isAnonymous) {
      $location.url('/welcome');
    }
  });
})

.controller('AnonDashCtrl', function($scope, $rootScope, $scope, Spiff, $location) {
  $scope.showLogin = function() {
    $rootScope.$broadcast('loginRequired');
  }

  $scope.$watch('Spiff.currentUser', function(user) {
    if (user && !user.isAnonymous) {
      $location.url('/');
    }
  });
});
