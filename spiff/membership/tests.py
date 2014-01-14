"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User, Group
import models
from spiff.payment.models import Payment
from spiff.api.tests import APITestMixin, withPermission, withLogin

class MemberTest(TestCase):
  def testUserCreation(self):
    u = User.objects.create_user('test', 'test@example.com', 'test')
    self.assertIsNotNone(u.member)
    self.assertEqual(u.member.user, u)
    u.delete()

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

  def testSearchFullname(self):
    ret = self.search(fullName='Test McTesterson')
    self.assertIn('objects', ret)
    self.assertEqual(len(ret['objects']), 1)

  def testSearchPartialFirst(self):
    ret = self.search(fullName='Test')
    self.assertIn('objects', ret)
    self.assertEqual(len(ret['objects']), 1)

  def testSearchPartialLast(self):
    ret = self.search(fullName='McTesterson')
    self.assertEqual(len(ret['objects']), 1)

  def testSearchPartialMultiple(self):
    guesterson = User.objects.create_user('guest', 'guest@example.com', 'guest')
    guesterson.first_name = 'Guest'
    guesterson.last_name = 'McGuesterson'
    guesterson.save()

    ret = self.search(fullName='esterson')
    self.assertIn('objects', ret)
    self.assertEqual(len(ret['objects']), 2)

class MemberAPITest(APITestMixin):
  def setUp(self):
    self.setupAPI()

  def testLogin(self):
    response = self.postAPIRaw('/v1/member/login/', {'username': 'test', 'password': 'test'})
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.cookies.has_key('sessionid'))

  def testBadLogin(self):
    response = self.postAPIRaw('/v1/member/login/', {'username': 'test',
      'password': 'nottest'})
    self.assertEqual(response.status_code, 401)
    self.assertFalse(response.cookies.has_key('sessionid'))

  def testDisabledLogin(self):
    self.user.is_active = False
    self.user.save()
    response = self.postAPIRaw('/v1/member/login/', {'username': 'test',
      'password': 'test'})
    self.assertEqual(response.status_code, 403)
    self.assertFalse(response.cookies.has_key('sessionid'))

  def testLogout(self):
    response = self.postAPIRaw('/v1/member/login/', {'username': 'test', 'password': 'test'})
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.cookies.has_key('sessionid'))
    session = response.cookies.get('sessionid')
    response = self.getAPIRaw('/v1/member/logout/')
    self.assertTrue(response.cookies.has_key('sessionid'))
    self.assertNotEqual(session, response.cookies.has_key('sessionid'))

  def testMissingPermission(self):
    response = self.postAPIRaw('/v1/member/self/has_permission/not.a_permission/')
    self.assertEqual(response.status_code, 403)

  @withPermission('membership.add_member')
  @withLogin
  def testHasPermission(self):
    response = self.postAPIRaw('/v1/member/self/has_permission/membership.add_member/')
    self.assertEqual(response.status_code, 204)
