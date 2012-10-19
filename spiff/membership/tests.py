"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User, Group
import models

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

class PaymentTest(TestCase):
  def setUp(self):
    self.user = User.objects.create_user('test', 'test@example.com', 'test')

  def tearDown(self):
    self.user.delete()

  def testCreation(self):
    p = models.DuePayment.objects.create(member=self.user.member, value=1)
    self.assertEqual(p.value, 1)
    self.assertEqual(len(self.user.member.payments.all()), 1)
