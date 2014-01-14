var spiffControllers = angular.module('spiffControllers', ['restangular', 'spiffApp', 'spiff']);

spiffControllers.controller('EpicenterCtrl', function($scope, $http, Spiff) {
  $scope.showLogin = function() {
    $('#loginModal').modal('show');
  };

  $scope.hideLogin = function() {
    $('#loginModal').modal('hide');
  };

  $scope.login = function() {
    var username = $('#username').val();
    var password = $('#password').val();
    Spiff.login(username, password).then(function() {
      $scope.hideLogin()
    });
  };

  $scope.logout = function() {
    Spiff.logout();
  };

  $scope.$on('loginRequired', function() {
    $scope.showLogin();
  });

  $http.get('/status.json').then(function (api) {
    console.log(api.data);
    $scope.spaceAPI = api.data;
  });
});

spiffControllers.controller('DashboardCtrl', function($scope, Restangular, Spiff, $location) {
  $scope.$watch('Spiff.currentUser', function(user) {
    if (user && !user.isAnonymous) {
      $scope.user = user;
      $scope.invoices = [];
      _.each(user.invoices, function(invoice) {
        $scope.invoices.push(Restangular.oneUrl('invoice', invoice).get().$object);
      });
    } else if (user && user.isAnonymous) {
      $location.url('/welcome');
    }
  });
});

spiffControllers.controller('AnonDashCtrl', function($scope, $rootScope, $scope, Spiff, $location) {
  $scope.showLogin = function() {
    $rootScope.$broadcast('loginRequired');
  }

  $scope.$watch('Spiff.currentUser', function(user) {
    if (user && !user.isAnonymous) {
      $location.url('/');
    }
  });
});

spiffControllers.controller('ResourceListCtrl', function($scope, Restangular) {
  $scope.resources = Restangular.all('resource').getList().$object;
});

spiffControllers.controller('ResourceCtrl', function($scope, Restangular, $routeParams) {
  var resource = Restangular.one('resource', $routeParams.resourceID);

  $scope.refreshResource = function() {
    resource.get().then(function (res) {
      $scope.resource = res;
    });
    $scope.refreshMetadata();
    $scope.refreshChangelog();
    $scope.refreshTrainings();
  }

  $scope.refreshMetadata = function() {
    resource.getList('metadata').then(function(meta) {
      $scope.metadata = meta;
    });
  }

  $scope.refreshChangelog = function() {
    resource.getList('changelog').then(function(log) {
      console.log(log[0]);
      $scope.changelog = log;
    });
  }

  $scope.refreshTrainings = function() {
    resource.getList('training').then(function(trainings) {
      console.log(trainings[0]);
      $scope.trainings = trainings;
    });
  }

  $scope.refreshResource();

  $scope.training = $scope.$new();
  $scope.training.pendingUsers = [];

  $scope.addTraining = function() {
    $('#trainingModal :input').attr('disabled', false);
    $('#trainingModal').modal('show');
  };

  $scope.closeTraining = function() {
    $('#trainingModal').modal('hide');
  };

  $scope.saveTraining = function() {
    $('#trainingModal :input').attr('disabled', true);
    $('#trainingModal').modal('hide');
    var rank = $('#trainingModal training-rank').val();

    var pendingCount = $scope.training.pendingUsers.length;

    _.each($scope.training.pendingUsers, function(pending) {
      console.log("Training "+pending);

      Restangular.all('training').post({
        resource: '/v1/resource/'+resource.id+'/',
        member: '/v1/member/'+pending.id+'/',
        rank: rank,
      }).then(function(trainings) {
        $scope.refreshTrainings();
        pendingCount--;
        if (pendingCount == 0)
          $scope.closeTraining();
      });
    });
  };

  $scope.addPendingUser = function() {
    var newUser = {searchName: $('#trainingModal #training-user').val(), id:-1};
    console.log("Adding new user");
    console.log(newUser);
    $('#trainingModel #training-user').val('');
    Restangular.all('member').search({fullName: newUser.searchName}).then(function(users) {
      if (users.objects.length > 0) {
        var user = users.objects[0];
        newUser.fullName = user.firstName+" "+user.lastName;
        newUser.id = user.id;
      }
    });
    $scope.training.pendingUsers.push(newUser);
  };

  $scope.forgetUser = function(user) {
    var newUsers = [];
    _.each($scope.training.pendingUsers, function(u) {
      if (u != user) {
        newUsers.push(u);
      }
    });
    $scope.training.pendingUsers = newUsers;
  };

  $scope.editMetadata = function(metaName) {
    $('#metadataEditorModal form')[0].reset();
    $('#metadataEditorModal #meta-id').val(-1);
    if (metaName != null) {
      var meta = _.findWhere($scope.metadata, {name: metaName});
      console.log(meta);
      $('#metadataEditorModal #meta-name').val(meta.name);
      $('#metadataEditorModal #meta-value').val(meta.value);
      $('#metadataEditorModal #meta-id').val(meta.id);
    }
    $('#metadataEditorModal :input').attr('disabled', false);
    $('#metadataEditorModal').modal('show');
  };

  $scope.deleteMetadata = function(meta) {
    Restangular.one('metadata', meta.id).remove().then(function() {
      $scope.refreshMetadata();
      $scope.refreshChangelog();
    });
  }

  $scope.saveMetadata = function() {
    $('#metadataEditorModal :input').attr('disabled', true);
    var id = $('#metadataEditorModal #meta-id').val();
    var value = $('#metadataEditorModal #meta-value').val();
    var name = $('#metadataEditorModal #meta-name').val();

    if (id > 0) {
      Restangular.one('metadata', id).patch({
        value: value,
        name: name,
        type: 0
      }).then(function(meta) {
        $scope.refreshMetadata();
        $scope.refreshChangelog();
        $scope.closeEditor();
      });
    } else {
      Restangular.all('metadata').post({
        resource: '/v1/resource/'+resource.id+'/',
        value: value,
        name: name,
        type: 0
      }).then(function(meta) {
        $scope.refreshMetadata();
        $scope.refreshChangelog();
        $scope.closeEditor();
      });
    }
  }

  $scope.closeEditor = function() {
    $('#metadataEditorModal').modal('hide');
  }
});

spiffControllers.controller('InvoiceCtrl', function($scope, Restangular, $routeParams) {
  $scope.invoice = Restangular.one('invoice', $routeParams.invoiceID).get().$object;
  $scope.showPayDialog = function() {
    $('#payInvoiceModal').modal('show');
  };

  $scope.closePayDialog = function() {
    $('#payInvoiceModal').modal('hide');
  };

  $scope.processCard = function() {
    $('#payInvoiceModal :input').attr('disabled', true);
    var card = $('#card_num').val();
    var cvc = $('#cvc').val();
    var month = $('#exp_month').val();
    var year = $('#exp_year').val();
    Restangular.all('payment').post({
      invoice: '/v1/invoice/'+$routeParams.invoiceID+'/',
      value: $('#inputPayment').val(),
      stripe: {
        card: card,
        cvc: cvc,
        exp_month: month,
        exp_year: year
      }
    }).then(function(payment) {
      $scope.invoice = Restangular.one('invoice', $routeParams.invoiceID).get().$object;
      $('#payInvoiceModal').modal('hide');
      $('#payInvoiceModal').reset();
    }).finally(function() {
      $('#payInvoiceModal :input').attr('disabled', false);
    });
  };
});
