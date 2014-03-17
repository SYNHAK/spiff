"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User, Group
import models
from spiff.api.tests import APITestMixin, withPermission, withLogin, withUser, withAdmin
import datetime
from spiff.subscription.models import SubscriptionPeriod, Subscription
from spiff.subscription import api as subscriptionAPI
import calendar
from spiff.payment.models import Invoice, Payment

class MembershipPeriodTest(APITestMixin):
  def setUp(self):
    self.setupAPI()

  @withAdmin
  def addOldDues(self):
    rank = self.createGroup('test').rank
    rank.monthlyDues = 15
    rank.save()

    self.postAPI('/v1/invoice/',
      {
        'user': self.user,
        'dueDate': datetime.date.today()
      }
    )

    self.postAPI('/v1/ranklineitem/',
      {
        'invoice': '/v1/invoice/1/',
        'rank': '/v1/rank/1/',
        'member': '/v1/member/1/',
        'activeFromDate': datetime.date.today(),
        'activeToDate': datetime.date.today(),
        'quantity': 1
      }
    )
    self.postAPI('/v1/payment/',
      {
        'invoice': '/v1/invoice/1/',
        'value': 15,
        'method': 0,
        'user': '/v1/user/1/'
      }
    )
    membershipPeriod = self.user.member.membershipPeriods.all()[0]
    self.assertEqual(membershipPeriod.activeFromDate.date(),
        datetime.date.today())
    self.assertEqual(membershipPeriod.activeToDate.date(), datetime.date.today())

  @withPermission('membership.read_member')
  @withPermission('auth.read_group')
  @withPermission('membership.create_membershipperiod')
  @withPermission('membership.read_rank')
  @withPermission('payment.create_invoice')
  @withPermission('payment.create_payment')
  @withPermission('subscription.read_subscriptionplan')
  @withAdmin
  def testSubscribeAndPayDues(self):
    rank = self.createGroup('test').rank
    rank.monthlyDues = 15
    rank.save()

    period = SubscriptionPeriod.objects.create(
      name = 'Monthly',
      dayOfMonth=1
    )

    plan = models.RankSubscriptionPlan.objects.create(
      rank = rank,
      member = self.user.member,
      period = period
    )

    self.postAPI('/v1/subscription/',
      {
        'user': '/v1/user/1/',
        'plan': '/v1/subscriptionplan/1/',
      }
    )

    self.assertEqual(len(self.user.invoices.all()), 0)
    subscriptionAPI.processSubscriptions()
    self.assertEqual(len(self.user.invoices.all()), 1)

    subscriptionAPI.processSubscriptions()
    self.assertEqual(len(self.user.invoices.all()), 1)

    self.postAPI('/v1/payment/',
      {
        'invoice': '/v1/invoice/1/',
        'value': 15,
        'method': 0,
        'user': '/v1/user/1/'
      }
    )

    self.assertTrue(self.user.groups.filter(name='test').exists())

    today = datetime.date.today()
    monthStart = datetime.date(year=today.year, month=today.month, day=1)
    monthEnd = datetime.date(year=today.year, month=today.month,
        day=calendar.monthrange(today.year, today.month)[1])
    monthEnd += datetime.timedelta(days=1)

    membershipPeriod = self.user.member.membershipPeriods.all()[0]
    self.assertEqual(membershipPeriod.activeFromDate.date(), monthStart)
    self.assertEqual(membershipPeriod.activeToDate.date(), monthEnd)

    subscriptionAPI.processSubscriptions()
    self.assertEqual(len(self.user.invoices.all()), 1)


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
    self.assertEqual(userCount, newUserCount)
    self.assertEqual(memberCount, newMemberCount)
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
    self.assertEqual(len(ret['objects']), 3)

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
