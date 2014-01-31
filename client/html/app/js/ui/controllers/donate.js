angular.module('spiff.donate', [
  'spiff',
  'restangular'
])

.controller('DonateCtrl', function($scope, Restangular) {
  $scope.plans = Restangular.all('donationplan').getList().$object;

  $scope.startSubscription = function(plan) {
    Restangular.all('subscription').post({
      plan: '/v1/subscriptionplan/'+plan.id+'/'
    });
  };
});
