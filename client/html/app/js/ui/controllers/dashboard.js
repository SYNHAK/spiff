angular.module('spiff.dashboard', [
  'restangular',
  'spiff'
])

.controller('SubscriptionCtrl', function($scope, Restangular, Spiff) {
  $scope.activeSubscriptions = Spiff.currentUser.subscriptions;
  var membershipPlans = Restangular.all('ranksubscriptionplan');
  $scope.membershipPlans = membershipPlans.getList().$object;

  $scope.close = $modalInstance.close;
})

.controller('RegistrationCtrl', function($scope, Restangular, Spiff, $modal) {
  $scope.$watch('Spiff.currentUser', function(user) {
    if (user && !user.isAnonymous) {
      $location.url('/');
    }
  });

  $scope.d = {};
  $scope.d.fields = [];
  $scope.requiredFields = [];
  $scope.optionalFields = [];
  Restangular.all('field').getList().then(function (fields) {
    _.each(fields, function(field) {
      if (field.required) {
        $scope.requiredFields.push(field);
      } else if (field.public && !field.protected){
        $scope.optionalFields.push(field);
      }
    });
  });

  $scope.submit = function() {
    var fields = [];
    _.each($scope.requiredFields, function(field) {
      fields.push({id: field.id, value: field.value});
    })
    _.each($scope.optionalFields, function(field) {
      fields.push({id: field.id, value: field.value});
    })

    Restangular.all('member').post({
      username: $scope.d.username,
      password: $scope.d.password,
      email: $scope.d.email,
      firstName: $scope.d.first_name,
      lastName: $scope.d.last_name,
      fields: fields
    }).then(function (u) {
      Spiff.login($scope.d.username, $scope.d.password).then(function (u) {
        $location.url('/');
      });
    });
  }
})


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

      $scope.openSubscriptionEditor = function() {
        $location.url('/members/self/subscriptions');
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
