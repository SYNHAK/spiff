var Spiff = angular.module('spiff', [
  'restangular'
]);

Spiff.factory('Spiff', function(Restangular, $http) {
  return {
    'currentUser': Restangular.one('member', userID).get(),
    'spaceAPI': $http.get('/status.json')
  };
});
