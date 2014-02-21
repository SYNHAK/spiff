angular.module('spiff.sensors', [
  'spiff',
  'restangular'
])

.controller('SensorListCtrl', function($scope, SpiffRestangular) {
  $scope.sensors = SpiffRestangular.all('sensor').getList().$object;
})

.controller('SensorCtrl', function($scope, SpiffRestangular, $routeParams) {
  var sensor = SpiffRestangular.one('sensor', $routeParams.sensorID);
  $scope.sensor = sensor.get().$object;
});

