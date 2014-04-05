#!/usr/bin/env python
import dateutil.parser
import datetime
from getpass import getpass
import sys
import logging
import argparse

from spiff import cli

parser = argparse.ArgumentParser()
cli.add_argument_group(parser)
parser.set_defaults(filter=['unpaid'])
parser.add_argument('-a', '--active', dest='filter', const='active', action='append_const')
parser.add_argument('-i', '--inactive', dest='filter', const='inactive', action='append_const')
parser.add_argument('-U', '--unpaid', dest='filter', const='unpaid', action='append_const')

args = parser.parse_args(sys.argv[1:])

api = cli.api_from_args(args)

subsTotal = 0
total = 0
inactive = []
active = []

for m in sorted(api.getList("member"), key=lambda x:x.outstandingBalance):
  if not m.activeMember:
    inactive.append(m)
  else:
    active.append(m)

if 'inactive' in args.filter:
  print "Inactive members (%s):"%(len(inactive))
  for m in inactive:
    print "%s: %s %s: %s"%(m.id, m.firstName, m.lastName, m.email)
    subs = api.getList("subscription", user=m.userid)
    print "\tSubscriptions:"
    for s in subs:
      print "\t\t%s: %s"%(s.id, s.plan['name'])
      subsTotal += s.plan['periodCost']
    if len(subs) == 0:
      print "\t\tNot subscribed!"

if 'inactive' in args.filter and 'active' in args.filter:
  print "----"

if 'active' in args.filter or 'unpaid' in args.filter:
  print "Active members (%s):"%(len(active))
  for m in active:
    if (m.outstandingBalance > 0 and 'unpaid' in args.filter) or 'unpaid' not in args.filter:
      print "%s: %s %s <%s>"%(m.id, m.firstName, m.lastName, m.email)
      print "\tMembership Periods:"
      if m.membershipRanges:
        for range in m.membershipRanges:
          print "\t\t%s to %s:"%(range['start'], range['end'])
      if m.outstandingBalance > 0:
        start = None
        end = None
        print "\tInvoices:"
        for i in sorted(api.getList("invoice", user=m.userid), key=lambda
            x:x.created):
          if i.unpaidBalance > 0:
            print "\t\t%s %s: %s"%(i.id, i.created, i.unpaidBalance)
            for l in api.getList("ranklineitem", invoice=i):
              lineStart = dateutil.parser.parse(l.activeFromDate)
              lineEnd = dateutil.parser.parse(l.activeToDate)
              if start is None or lineStart < start:
                start = lineStart
              if end is None or lineEnd > end:
                end = lineEnd
              if end.date().month == start.date().month:
                end += datetime.timedelta(days=1)
                l.activeToDate = end
                l.save()
        total += m.outstandingBalance
        print "\tDues owed for %s through %s: %s"%(start.date(), end.date(), m.outstandingBalance)
      subs = api.getList("subscription", user=m.userid)
      print "\tTotal credit available: %s"%(m.availableCredit)
      print "\tSubscriptions:"
      for s in subs:
        print "\t\t%s: %s"%(s.id, s.plan['name'])
        subsTotal += s.plan['periodCost']
      if len(subs) == 0:
        print "\t\tNot subscribed!"

print "----"
print "Grand total: %s"%(total)
print "Monthly total: %s"%(subsTotal)
