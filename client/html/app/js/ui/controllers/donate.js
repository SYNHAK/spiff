angular.module('spiff.donate', [
  'spiff',
  'restangular',
  'spaceapi'
])

.controller('AddDonationSubscriptionCtrl', function($scope, SpiffRestangular, Spiff, $modalInstance, plan) {
  $scope.plan = plan;
  $scope.cancel = $modalInstance.close;
  $scope.save = function() {
    SpiffRestangular.all('subscription').post({
      plan: '/v1/subscriptionplan/'+plan.id+'/',
      user: '/v1/user/'+Spiff.currentUser.userid+'/',
    }).then(function() {
      $modalInstance.close();
    });
  }
})

.controller('DonateCtrl', function($scope, SpiffRestangular, SpaceAPI, Spiff, $modal) {
  $scope.plans = SpiffRestangular.all('donationplan').getList().$object;

  SpaceAPI.ready(function(api) {
    $scope.spaceAPI = api;
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
