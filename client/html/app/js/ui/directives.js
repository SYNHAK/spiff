var spiffDirectives = angular.module('spiffDirectives', [
]);

spiffDirectives.directive('qrCode', function($location) {
  return {
    link: function(scope, element, attrs) {
      var size = 80;
      if (attrs.size != undefined) {
        size = attrs.size;
      }
      console.log("Making size " +size);
      if (attrs.qrCode == undefined) {
        $(element).qrcode({
          text: attrs.text,
          width: size,
          height: size,
          maxVersion: 4,
        });
      } else {
        $(element).qrcode({
          text: attrs.text,
          width: size,
          height: size,
          ecLevel: 'H',
          render: 'div'
        });
      }
    }
  }
});
