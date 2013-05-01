#!/usr/bin/env python
import spiff
import logging
logging.basicConfig(level=logging.DEBUG)

api = spiff.API("https://synhak.org/auth/", verify=False)

for res in api.resources():
    print type(res)
    print res.type
