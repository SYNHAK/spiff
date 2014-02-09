angular.module('spiff.donate', [
  'spiff',
  'restangular'
])

.controller('AddDonationSubscriptionCtrl', function($scope, Restangular, Spiff, $modalInstance, plan) {
  $scope.plan = plan;
  $scope.cancel = $modalInstance.close;
  $scope.save = function() {
    Restangular.all('subscription').post({
      plan: '/v1/subscriptionplan/'+plan.id+'/',
      user: '/v1/user/'+Spiff.currentUser.userid+'/',
    }).then(function() {
      $modalInstance.close();
    });
  }
})

.controller('DonateCtrl', function($scope, Restangular, Spiff, $http, $modal) {
  $scope.plans = Restangular.all('donationplan').getList().$object;

  $http.get('/status.json').then(function (api) {
    $scope.spaceAPI = api.data;
  });

  $scope.startSubscription = function(plan) {
    if (Spiff.currentUser.isAnonymous) {
      $modal.open({
        templateUrl: 'donate/modal/login-needed.html',
        controller: function($location, $scope, $modalInstance) {
          $scope.cancel = $modalInstance.close;
          $scope.start = function() {
            $modalInstance.close();
            $location.url('/register');
          }
        }
      });
    } else {
      $modal.open({
        templateUrl: 'donate/modal/add.html',
        controller: 'AddDonationSubscriptionCtrl',
        resolve: {plan: function() {return plan}}
      })
    }
  };
});
