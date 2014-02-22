angular.module('spiff.resources', [
  'spiff',
  'restangular',
])

.controller('ResourceListCtrl', function($scope, SpiffRestangular, $state) {
  $scope.resources = [];
  $scope.$state = $state;

  $scope.gotoPage = function(pagenum) {
    var count = 20;
    var offset = pagenum * count;
    SpiffRestangular.all('resource').getList({'limit': count, 'offset': offset}).then(function(resources) {
      $scope.resources = resources;
    });
  };

  $scope.gotoPage(0);
})

.controller('ResourceMetadataEditCtrl', function($scope, $modalInstance, SpiffRestangular, resource, currentMetadata) {
  $scope.d = {};

  if (currentMetadata) {
    $scope.d.name = currentMetadata.name;
    $scope.d.value = currentMetadata.value;
  }

  $scope.save = function() {
    var value = $scope.d.value;
    var name = $scope.d.name;

    if (currentMetadata) {
      SpiffRestangular.one('metadata', currentMetadata.id).patch({
        value: value,
        name: name,
        type: 0
      }).then(function(meta) {
        $modalInstance.close();
      });
    } else {
      SpiffRestangular.all('metadata').post({
        resource: '/v1/resource/'+resource.id+'/',
        value: value,
        name: name,
        type: 0
      }).then(function(meta) {
        $modalInstance.close();
      });
    }
  }

  $scope.close = function() {$modalInstance.close()};
})

.controller('ResourceCtrl', function($scope, SpiffRestangular, $stateParams, $state, $modal) {
  var resource = SpiffRestangular.one('resource', $stateParams.resourceID);
  $scope.resource = resource;

  $scope.$state = $state;

  $scope.refreshResource = function() {
    resource.get().then(function (res) {
      $scope.resource = res;
    });
    $scope.refreshMetadata();
    $scope.refreshChangelog();
    $scope.refreshTrainings();
  }

  $scope.refreshMetadata = function() {
    SpiffRestangular.all('metadata').getList({resource: resource.id}).then(function(meta) {
      $scope.metadata = meta;
    });
  }

  $scope.refreshChangelog = function() {
    SpiffRestangular.all('changelog').getList({resource: resource.id}).then(function(log) {
      $scope.changelog = log;
    });
  }

  $scope.refreshTrainings = function() {
    SpiffRestangular.all('training').getList({resource: resource.id}).then(function(trainings) {
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

      SpiffRestangular.all('training').post({
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
    SpiffRestangular.all('member').search({fullName: newUser.searchName}).then(function(users) {
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
    var current = null;
    if (metaName != null) {
      current = _.findWhere($scope.metadata, {name: metaName});
    }
    var modal = $modal.open({
      templateUrl: 'resources/modal/edit-metadata.html',
      controller: 'ResourceMetadataEditCtrl',
      resolve: {
        resource: function() {return resource},
        currentMetadata: function() {return current}
      }
    });
    modal.result.then(function() {
      $scope.refreshMetadata();
      $scope.refreshChangelog();
    });
  };

  $scope.deleteMetadata = function(meta) {
    SpiffRestangular.one('metadata', meta.id).remove().then(function() {
      $scope.refreshMetadata();
      $scope.refreshChangelog();
    });
  }
});
