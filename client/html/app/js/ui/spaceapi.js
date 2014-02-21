var SpaceAPI = angular.module('spaceapi', [
]);

SpaceAPI.provider('SpaceAPI', function() {
  var baseUrl = '/';
  this.setBaseUrl = function(url) {
    baseUrl = url;
  };

  this.$get = function($http, $q) {
    var configDeferred = $q.defer();
    $http.get(baseUrl).then(function(data) {
      configDeferred.resolve(data);
    });
    return {
      ready: configDeferred.promise.then,
    };
  };
});
