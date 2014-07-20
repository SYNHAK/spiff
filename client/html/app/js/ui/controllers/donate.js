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

.controller('DonationRegistrationCtrl', function($scope, $modal, SpiffRestangular, $stateParams) {
  var plan = SpiffRestangular.one('donationplan', $stateParams.planID);
  $scope.$watch('Spiff.currentUser', function(user) {
    if (user && !user.isAnonymous) {
      $modal.open({
        templateUrl: 'donate/modal/add.html',
        controller: 'AddDonationSubscriptionCtrl',
        resolve: {plan: function() {return plan}}
      });
    }
  });
})

.controller('DonateCtrl', function($scope, SpiffRestangular, SpaceAPI, Spiff, $modal, $location) {
  $scope.plans = SpiffRestangular.all('donationplan').getList().$object;

  SpaceAPI.ready(function(api) {
    $scope.spaceAPI = api.data;
  });

  $scope.startSubscription = function(plan) {
    if (Spiff.currentUser.isAnonymous) {
      $location.url('/donate/register/'+plan.id);
    } else {
      $modal.open({
        templateUrl: 'donate/modal/add.html',
        controller: 'AddDonationSubscriptionCtrl',
        resolve: {plan: function() {return plan}}
      })
    }
  };
});
