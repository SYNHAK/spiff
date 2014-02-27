"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User, Group
import models
from spiff.api.tests import APITestMixin, withPermission, withLogin, withUser
import datetime

class MembershipPeriodTest(APITestMixin):
  def setUp(self):
    self.setupAPI()

  @withPermission('membership.read_member')
  @withPermission('auth.read_group')
  @withPermission('membership.create_membershipperiod')
  @withPermission('membership.read_rank')
  def testCreateCurrentPeriod(self):
    self.createGroup('test')
    self.postAPI('/v1/membershipperiod/',
      {
        'member': '/v1/member/1/',
        'rank': '/v1/rank/1/',
        'start': str(datetime.date.today()-datetime.timedelta(days=-7)),
        'end': str(datetime.date.today()+datetime.timedelta(days=7))
      }
    )


class AnonymousUserMiddlewareTest(APITestMixin):
  def setUp(self):
    self.setupClient()

  def testFetchAnon(self):
    user = self.getAPI('/v1/member/self/')
    self.assertNotEqual(user, None)

class MemberTest(TestCase):
  def testUserCreation(self):
    u = User.objects.create_user('test', 'test@example.com', 'test')
    self.assertIsNotNone(u.member)
    self.assertEqual(u.member.user, u)
    u.delete()

  def testCreateAnonUser(self):
    userCount = len(User.objects.all())
    memberCount = len(models.Member.objects.all())
    anonUser = models.get_anonymous_user()
    newUserCount = len(User.objects.all())
    newMemberCount = len(models.Member.objects.all())
    self.assertNotEqual(userCount, newUserCount)
    self.assertNotEqual(memberCount, newMemberCount)
    self.assertEqual(models.get_anonymous_user().pk, anonUser.pk)

  def testRecreateAnonMember(self):
    user = models.get_anonymous_user()
    user.member.delete()
    member = None
    with self.assertRaises(models.Member.DoesNotExist):
      member = User.objects.get(id=user.pk).member
    user = models.get_anonymous_user()
    self.assertEqual(user.member.user_id, user.id)
    self.assertEqual(member, None)

class RankTest(TestCase):
  def testGroupCreation(self):
    g = Group.objects.create(name="Test Group")
    self.assertIsNotNone(g.rank)
    self.assertEqual(g.rank.group, g)
    g.delete()

class MemberSearchAPITest(APITestMixin):
  def setUp(self):
    self.setupAPI()

  def search(self, status=200, **kwargs):
    return self.getAPI('/v1/member/search/', kwargs, status=status)

  @withUser
  def testSearchFullname(self):
    ret = self.search(fullName='Test McTesterson')
    self.assertIn('objects', ret)
    self.assertEqual(len(ret['objects']), 1)

  @withUser
  def testSearchPartialFirst(self):
    ret = self.search(fullName='Test')
    self.assertIn('objects', ret)
    self.assertEqual(len(ret['objects']), 1)

  @withUser
  def testSearchPartialLast(self):
    ret = self.search(fullName='McTesterson')
    self.assertEqual(len(ret['objects']), 1)

  @withUser
  def testSearchPartialMultiple(self):
    guesterson = self.createUser('guest', 'guest')
    guesterson.first_name = 'Guest'
    guesterson.last_name = 'McGuesterson'
    guesterson.save()

    ret = self.search(fullName='esterson')
    self.assertIn('objects', ret)
    self.assertEqual(len(ret['objects']), 2)

class MemberAPITest(APITestMixin):
  def setUp(self):
    self.setupAPI()

  @withUser
  def testLogin(self):
    response = self.postAPI('/v1/member/login/', {'username': 'test',
      'password': 'test'}, status=200)
    self.assertTrue('token' in response)

  @withUser
  def testBadLogin(self):
    response = self.postAPI('/v1/member/login/', {'username': 'test',
      'password': 'nottest'}, status=401)
    self.assertIsNone(response)

  @withUser
  def testDisabledLogin(self):
    self.user.is_active = False
    self.user.save()
    response = self.postAPI('/v1/member/login/', {'username': 'test',
      'password': 'test'}, status=403)
    self.assertIsNone(response)

  def testMissingPermission(self):
    response = self.postAPIRaw('/v1/member/self/has_permission/not.a_permission/')
    self.assertEqual(response.status_code, 403)

  @withPermission('membership.add_member')
  @withLogin
  def testHasPermission(self):
    response = self.postAPIRaw('/v1/member/self/has_permission/membership.add_member/')
    self.assertEqual(response.status_code, 204)
