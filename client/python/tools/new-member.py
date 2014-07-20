#!/usr/bin/env python
import spiff
from getpass import getpass
import sys
import logging
logging.basicConfig(level=logging.WARNING)

api = spiff.API(sys.argv[1], verify=False)
api.login(raw_input('Username: '), getpass())

firstName = raw_input("First Name: ")
lastName = raw_input("Last Name: ")
email = raw_input("Email: ")

print "Add subscription:"
for plan in api.getList('subscriptionplan'):
  print "%s: %s"%(plan.id, plan.name)
plan_id = raw_input("ID: ")

print "Set rank:"
for group in api.getList('group'):
  print "%s: %s"%(group.id, group.name)
group_id = raw_input("Group: ")

member = api.create('member',
  firstName = firstName,
  lastName = lastName,
  email = email,
  username = email.split('@')[0],
  password = None,
  groups = ['/v1/group/'+group_id]
)

api.create('subscription',
  user = '/v1/user/'+member.id,
  plan = '/v1/subscriptionplan/%s'%(plan_id)
)
