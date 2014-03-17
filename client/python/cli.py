#!/usr/bin/env python
import spiff
from getpass import getpass
import sys
import logging
import json
import os

if 'SPIFF_API' in os.environ:
  uri = os.environ['SPIFF_API']
else:
  uri = sys.argv[1]
api = spiff.API(uri, verify=False)
api.login(raw_input("Username: "), getpass())

cmd = sys.argv[2]

def printObj(obj, formats=[]):
  if len(formats) == 0:
    print "%s:"%(obj.resource_uri)
    for attr in obj.attributes:
      print "\t%s: %s"%(attr, getattr(obj, attr))
  else:
    attrs = {}
    for attr in obj.attributes:
      attrs[attr] = getattr(obj, attr)
    for fmt in formats:
      print fmt%attrs

if cmd == "list":
  objType = sys.argv[3]
  filters = {}
  formats = []
  for filterParam in sys.argv[4:]:
    if "=" in filterParam:
      param, value = filterParam.split('=')
      filters[param] = value
    else:
      formats.append(filterParam)
  for obj in api.getList(objType, **filters):
    printObj(obj, formats)
elif cmd == "get":
  objType = sys.argv[3]
  id = sys.argv[4]
  formats = sys.argv[5:]
  printObj(api.getOne("v1/%s/"%(objType), id), formats)
elif cmd == "update":
  objType = sys.argv[3]
  id = sys.argv[4]
  obj = api.getOne("v1/%s/"%(objType), id)
  props = {}
  for propParam in sys.argv[5:]:
    param, value = propParam.split('=')
    setattr(obj, param, json.loads(value))
  obj.save()
