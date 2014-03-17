angular.module('spiff.members', [
  'spiff',
  'restangular',
  'ui.bootstrap.progressbar',
  'template/progressbar/progressbar.html'
])

.controller('MemberPaymentCtrl', function($scope, $modal, $stateParams, SpiffRestangular, Spiff) {
  var user = SpiffRestangular.one('member', $stateParams.memberID);
  var payments = SpiffRestangular.all('payment');
  var invoices = SpiffRestangular.all('invoice');

  function refreshCards() {
    return user.getStripeCards().then(function (cards) {
      var cardList = [];
      _.each(cards.cards, function(c) {
        cardList.push(c);
      });
      $scope.stripeCards = cardList;
    });
  }

  function refresh() {
    user.get().then(function(user) {
      $scope.user = user;
    });
    invoices.getList({'user': user.id}).then(function(invoices) {
      $scope.invoices = invoices;
    });
    payments.getList({'user': user.id}).then(function(payments) {
      $scope.payments = payments;
    });

    refreshCards();
  }

  $scope.stripeCards = null;

  $scope.addPaymentCard = function() {
    var modal = $modal.open({
      templateUrl: 'dashboard/modal/add-payment-card.html',
      controller: 'AddPaymentCardCtrl',
      resolve: {user: function() {return user}}
    });
    modal.result.then(function() {
      $scope.refreshCards();
    });
  }

  $scope.removeCard = function(card) {
    user.one('stripeCards', card.id).remove().then(function() {
      $scope.refreshCards();
    });
  }

  refresh();
})

.controller('ConfirmSubscriptionChangesCtrl', function($scope, additions, removals, user, $modalInstance, SpiffRestangular) {
  $scope.additions = additions;
  $scope.removals = removals;
  $scope.close = $modalInstance.close;
  $scope.pending = 0;
  $scope.save = function() {
    _.each(removals, function(subscription) {
      $scope.pending++;
      SpiffRestangular.one('subscription', subscription.id).remove().then(function() {
        $scope.pending--;
        if ($scope.pending == 0)
          $modalInstance.close();
      });
    });
    _.each(additions, function(addition) {
      $scope.pending++;
      console.log(user);
      SpiffRestangular.all('subscription').post({
        plan: '/v1/subscriptionplan/'+addition.id+'/',
        user: '/v1/user/'+user.userid+'/'
      }).then(function() {
        $scope.pending--;
        if ($scope.pending == 0)
          $modalInstance.close();
      });
    });
  }
})

.controller('SubscriptionCtrl', function($scope, $modal, $stateParams, SpiffRestangular, Spiff) {
  var user = SpiffRestangular.one('member', $stateParams.memberID);
  function refresh() {
    user.get().then(function (u) {
      $scope.user = u;
      $scope.activeSubscriptions = u.subscriptions;
    });
    $scope.pendingAdditions = [];
    $scope.pendingRemovals = [];
  }

  refresh();

  var groups = SpiffRestangular.all('group');
  groups.getList().then(function(groups) {
    $scope.availableGroups = groups;
  });

  $scope.availablePlans = [];

  var membershipPlans = SpiffRestangular.all('ranksubscriptionplan');
  membershipPlans.getList().then(function(plans) {
    _.each(plans, function(p) {
      $scope.availablePlans.push(p);
    });
  });

  var donationPlans = SpiffRestangular.all('donationplan');
  donationPlans.getList().then(function(plans) {
    _.each(plans, function(p) {
      $scope.availablePlans.push(p);
    });
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
        user: function() {return $scope.user;}
      }
    });
    modal.result.then(function() {
      refresh();
    });
  }
})


.controller('MemberListCtrl', function($scope, SpiffRestangular) {
  $scope.groups = []
  SpiffRestangular.all('group').getList().then(function (groups) {
    _.each(groups, function(group) {
      group.members = [];
      $scope.groups.push(group);
      SpiffRestangular.all('member').getList({'groups__in': group.id}).then(function(members) {
        group.members = members;
      });
    });
  });
  $scope.members = SpiffRestangular.all('member').getList().$object;
})

.controller('MemberViewCtrl', function($scope, SpiffRestangular, $stateParams) {
  var member = SpiffRestangular.one('member', $stateParams.memberID);
  member.get().then(function (member) {
    $scope.member = member;
    $scope.periods = member.membershipRanges;
    SpiffRestangular.all('group').getList().then(function (groups) {
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
