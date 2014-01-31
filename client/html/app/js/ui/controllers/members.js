angular.module('spiff.members', [
  'spiff',
  'restangular'
])

.controller('MemberListCtrl', function($scope, Restangular) {
  $scope.groups = []
  Restangular.all('group').getList().then(function (groups) {
    _.each(groups, function(group) {
      group.members = [];
      $scope.groups.push(group);
      group.getMembers().then(function (members) {
        console.log(members);
        group.members = members.objects;
      });
    });
  });
  $scope.members = Restangular.all('member').getList().$object;
})

.controller('MemberCtrl', function($scope, Restangular, $routeParams) {
  var member = Restangular.one('member', $routeParams.memberID);
  member.get().then(function (member) {
    $scope.member = member;
    console.log(member.groups);
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
    console.log(newGroups);

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
