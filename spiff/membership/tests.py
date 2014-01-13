"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User, Group
import models
from spiff.payment.models import Payment

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
