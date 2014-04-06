#!/usr/bin/env python
from getpass import getpass
import sys
import logging
logging.basicConfig(level=logging.WARNING)

from spiff import cli

METHODS = {
    'cash': 0,
    'check': 1,
    'stripe': 2,
    'other': 3,
    'credit': 4
}

parser = cli.argparser()
parser.add_argument('id', nargs='?', default=[], action='append')
parser.add_argument('--method', default='cash', help='Method of payment')

api, args = cli.api_from_argv(parser=parser)

for id in args.id:
  invoice = api.getOne('invoice', id)
  print "Marking invoice %s as paid via %s..."%(invoice.id, args.method)
  payment = api.create('payment',
    invoice = invoice,
    value = invoice.unpaidBalance,
    method = METHODS[args.method],
    user = invoice.user
  )
  print "- Created payment %s"%(payment.id)
