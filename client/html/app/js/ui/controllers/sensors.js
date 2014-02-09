angular.module('spiff.sensors', [
  'spiff',
  'restangular'
])

.controller('SensorListCtrl', function($scope, Restangular) {
  $scope.sensors = Restangular.all('sensor').getList().$object;
})

.controller('SensorCtrl', function($scope, Restangular, $routeParams) {
  var sensor = Restangular.one('sensor', $routeParams.sensorID);
  $scope.sensor = sensor.get().$object;
});

