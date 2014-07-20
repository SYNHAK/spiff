#!/usr/bin/env python
from spiff import cli
import sys

api = cli.api_from_argv()

with open(sys.argv[1], 'r') as csvfile:
    reader = csv.reader(csvfile)
