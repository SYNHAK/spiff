#!/usr/bin/env python
import spiff
from getpass import getpass
import sys
import logging
logging.basicConfig(level=logging.WARNING)

api = spiff.API(sys.argv[1], verify=False)
api.login(raw_input("Username: "), getpass())

m = api.getOne("v1/member", sys.argv[2])
print m.groups
