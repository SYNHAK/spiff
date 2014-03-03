angular.module('messages', [])

.provider('Messages', function($rootScope) {
  var messages = [];
  this.$get = function($rootScope) {
    var scope = $rootScope.$new();
    scope.messages = messages;
    scope.info = function(text) {
      messages.push({'text': text});
      scope.messages = messages;
    };
    return scope;
  }
})

.controller('MessagesCtrl', function($scope, Messages) {
  $scope.messages = Messages;
});
