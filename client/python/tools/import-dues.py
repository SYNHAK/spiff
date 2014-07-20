#!/usr/bin/env python
import datetime
import sys
import spiff
import logging
import csv
import calendar
from getpass import getpass

logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('spiff').setLevel(logging.INFO)
#logging.basicConfig(level=logging.DEBUG)

api = spiff.API(sys.argv[1], verify=False)
api.login(raw_input("Username: "), getpass())

grandTotal = 0
monthlyDues = 0
memberCount = 0

with open('/home/tdfischer/Projects/synhak/dues.csv', 'r') as csvfile:
  reader = csv.reader(csvfile)
  for row in reader:
    try:
      firstName, lastName = row[0].split(' ')
    except ValueError:
      continue
    rate = int(row[-3])
    if row[35] == "":
      start = datetime.date(year=2012, month=5, day=1)
    else:
      split = map(int, row[35].split('/'))
      start = datetime.date(year=2000+split[2], month=split[0], day=split[1])
    if row[34] == "":
      end = datetime.date.today()
      monthlyDues += rate
      memberCount += 1
    else:
      split = map(int, row[34].split('/'))
      end = datetime.date(year=2000+split[2], month=split[0], day=split[1])
    startIdx = (start.year-2012)*12+start.month+1
    endIdx = (end.year-2012)*12+end.month+1

    try:
      ranks = api.getList('rank', monthlyDues=rate)
      rank = ranks[0]
    except KeyError:
      print "Could not find what rank where %s %s pays $%s/mo"%(firstName,
          lastName, rate)
      continue

    group = api.get(rank.group)

    members = api.getList('member', firstName=firstName,
        lastName=lastName)
    if len(members) == 0:
      groups = [group]
      email = row[1]
      if email == "":
        continue
      print "Adding %s %s to %s"%(firstName, lastName, group['name'])
      member = api.create('member',
        firstName = firstName,
        lastName = lastName,
        email = email,
        username = email.split('@')[0],
        password = None,
        groups = groups
      )
    else:
      member = members[0]
    sys.stdout.write("%s %s: "%(member['firstName'], member['lastName']))
    sys.stdout.write("From %s to %s:\t"%(start, end))
    cursor = start
    count = 0
    for c in row[startIdx:endIdx]:
      cursorEndDay = calendar.monthrange(cursor.year, cursor.month)[1]
      cursorEnd = datetime.date(year=cursor.year, month=cursor.month,
          day=cursorEndDay)
      in30Days = datetime.date.today()+datetime.timedelta(days=30)

      if c != '-':
        periods = api.getList('membershipperiod',
          rank = rank,
          member = member,
          start = cursor,
          end = cursorEnd
        )

        openLineItems = api.getList('ranklineitem',
          rank = rank,
          member = member,
          activeFromDate = cursor,
          activeToDate = cursorEnd
        )

        sys.stdout.write("\t%s/%s "%(cursor.year, cursor.month))
        sys.stdout.flush()

        if len(periods) == 0 and len(openLineItems) == 0:
          invoice = api.create('invoice',
            user = member.user,
            dueDate = in30Days
          )
          lineItem = api.create('ranklineitem',
            rank = rank,
            member = member,
            activeFromDate = cursor,
            activeToDate = cursorEnd,
            invoice = invoice,
            quantity = 1
          )

          invoice = api.getOne(invoice)

          if c == '*':
            payment = api.create('payment',
              invoice = invoice,
              value = invoice.unpaidBalance,
              method = 0,
              user = member.user
            )
            invoice.draft = False
            invoice.save()
            sys.stdout.write("P")
          else:
            sys.stdout.write("I*")
            invoice.draft = False
            invoice.open = True
            invoice.save()
            count +=1 
        elif len(periods) == 0:
          sys.stdout.write("I")
        else:
          sys.stdout.write("P")
      newYear = cursor.year
      newMonth = cursor.month+1
      if newMonth == 13:
        newMonth = 1
        newYear = newYear+1
      cursor = datetime.date(year=newYear, month=newMonth, day=1)
    member = api.getOne(member)
    sys.stdout.write("\n\tTotal: %s @ $%s =\t$%s\n"%(count, rate,
      member.outstandingBalance))
    grandTotal += member.outstandingBalance
  print "Grand total: $%s"%(grandTotal)
  print "Monthly dues: $%s"%(monthlyDues)
  print "Total members: %s"%(memberCount)
