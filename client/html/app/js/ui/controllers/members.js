angular.module('spiff.members', [
  'spiff',
  'restangular',
  'ui.bootstrap.progressbar',
  'template/progressbar/progressbar.html'
])

.controller('ConfirmSubscriptionChangesCtrl', function($scope, additions, removals, user, $modalInstance, Restangular) {
  $scope.additions = additions;
  $scope.removals = removals;
  $scope.close = $modalInstance.close;
  $scope.pending = 0;
  $scope.save = function() {
    _.each(removals, function(subscription) {
      $scope.pending++;
      Restangular.one('subscription', subscription.id).remove().then(function() {
        $scope.pending--;
        if ($scope.pending == 0)
          $modalInstance.close();
      });
    });
    _.each(additions, function(addition) {
      $scope.pending++;
      Restangular.all('subscription').post({
        plan: '/v1/subscriptionplan/'+addition.id+'/',
        user: '/v1/member/'+user.id+'/'
      }).then(function() {
        $scope.pending--;
        if ($scope.pending == 0)
          $modalInstance.close();
      });
    });
  }
})

.controller('MembershipCtrl', function($scope, $modal, $stateParams, Restangular, Spiff) {
  var user = Restangular.one('member', $stateParams.memberID);
  function refresh() {
    user.get().then(function (u) {
      $scope.user = u;
      $scope.activeSubscriptions = u.subscriptions;
    });
    $scope.pendingAdditions = [];
    $scope.pendingRemovals = [];
  }

  refresh();

  var membershipPlans = Restangular.all('ranksubscriptionplan');
  membershipPlans.getList().then(function(plans) {
    $scope.membershipPlans = plans;
    console.log(plans[0]);
  });

  $scope.addSubscription = function(plan) {
    $scope.pendingAdditions.push(plan);
  }

  $scope.removeSubscription = function(idx) {
    $scope.pendingRemovals.push($scope.activeSubscriptions[idx]);
    $scope.activeSubscriptions.splice(idx, 1);
  }

  $scope.removePendingAddition = function(idx) {
    $scope.pendingAdditions.splice(idx, 1);
  }

  $scope.removePendingRemoval = function(idx) {
    $scope.activeSubscriptions.push($scope.pendingRemovals[idx]);
    $scope.pendingRemovals.splice(idx, 1);
  }

  $scope.save = function() {
    var modal = $modal.open({
      templateUrl: 'members/modal/confirm-subscription-changes.html',
      controller: 'ConfirmSubscriptionChangesCtrl',
      resolve: {
        removals: function() {return $scope.pendingRemovals;},
        additions: function() {return $scope.pendingAdditions;},
        user: function() {return user;}
      }
    });
    modal.result.then(function() {
      refresh();
    });
  }
})


.controller('MemberListCtrl', function($scope, Restangular) {
  $scope.groups = []
  Restangular.all('group').getList().then(function (groups) {
    _.each(groups, function(group) {
      group.members = [];
      $scope.groups.push(group);
      group.getMembers().then(function (members) {
        group.members = members.objects;
      });
    });
  });
  $scope.members = Restangular.all('member').getList().$object;
})

.controller('MemberViewCtrl', function($scope, Restangular, $stateParams) {
  var member = Restangular.one('member', $stateParams.memberID);
  member.get().then(function (member) {
    $scope.member = member;
    Restangular.all('group').getList().then(function (groups) {
      $scope.availableGroups = groups;
      _.each(groups, function(group) {
        if (_.find(member.groups, function(g) {return g.id == group.id;})) {
          group.active = true;
        } else {
          group.active = false;
        }
      });
    });
  });

  $scope.saveGroups = function() {
    var newGroups = [];
    $('#groups-form input[type="checkbox"]:checked').each(function(idx, c) {
      newGroups.push("/v1/group/"+$(c).val()+"/");
    });

    member.patch({'groups': newGroups}).then(function() {
      $('#modifyGroupsModal').modal('hide');
    });
  }

  $scope.showModifyGroups = function() {
    $('#modifyGroupsModal').modal('show');
  }

  $scope.hideModifyGroups = function() {
    $('#modifyGroupsModal').modal('hide');
  }
});
