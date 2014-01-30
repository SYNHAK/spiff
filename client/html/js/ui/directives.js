var spiffDirectives = angular.module('spiffDirectives', [
]);

spiffDirectives.directive('qrCode', function($location) {
  return {
    link: function(scope, element, attrs) {
      if (attrs.qrCode == undefined) {
        $(element).qrcode({
          text: $location.absUrl(),
          maxVersion: 4
        });
      } else {
        $(element).qrcode({
          text: $location.absUrl(),
          size: 80,
          ecLevel: 'H',
          render: 'div'
        });
      }
    }
  }
});
