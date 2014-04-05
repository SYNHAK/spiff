#!/usr/bin/env python
from spiff import cli

import sys
import logging
import json
import argparse

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

class Command(object):
    def __init__(self, api, args):
        super(Command, self).__init__()
        self.args = args
        self.api = api

    @staticmethod
    def name():
        raise NotImplemented

    @staticmethod
    def addArgs(parser):
        pass

    def run(self):
        raise NotImplemented()

class ListCommand(Command):
    def __init__(self, api, args):
        super(ListCommand, self).__init__(api, args)
    
    def run(self):
        objType = self.args.type
        filters = {}
        formats = []

        for filterParam in self.args.format_or_param:
            if "=" in filterParam:
                param, value = filterParam.split('=')
                filters[param] = value
            else:
                formats.append(filterParam)

        for obj in self.api.getList(objType, **filters):
            printObj(obj, formats)

    @staticmethod
    def name():
        return "list"

    @staticmethod
    def addArgs(parser):
        parser.add_argument('type')
        parser.add_argument('format_or_param', nargs='*', default=[],
        action='append')

class GetCommand(Command):
    def run(self):
        objType = self.args.type
        id = self.args.id
        formats = self.args.format
        printObj(self.api.getOne(objType, id), formats)

    @staticmethod
    def name():
        return "get"

    @staticmethod
    def addArgs(parser):
        parser.add_argument('type')
        parser.add_argument('id')
        parser.add_argument('format', nargs='?', default=[], action='append')

class UpdateCommand(Command):
    def run(self):
        objType = self.args.type
        id = self.args.id
        params = self.args.property
        obj = self.api.getOne(objType, id)
        props = {}
        for propParam in params:
            param, value = propParam.split('=')
            setattr(obj, param, json.loads(value))
        obj.save()

    @staticmethod
    def name():
        return "update"

    @staticmethod
    def addArgs(parser):
        parser.add_argument('type')
        parser.add_argument('id')
        parser.add_argument('property', nargs='*', default=[], action='append')

class CreateCommand(Command):
    def run(self):
        objType = self.args.type
        props = {}
        for propParam in self.args.property:
            param, value = propParam.split('=')
            try:
                props[param] = json.loads(value)
            except ValueError:
                props[param] = value
        self.api.create(objType, **props)

    @staticmethod
    def name():
        return "create"

    @staticmethod
    def addArgs(parser):
        parser.add_argument('type')
        parser.add_argument('property', nargs='*', default=[], action='append')

class DeleteCommand(Command):
    def run(self):
        objType = self.args.type
        id = self.args.id
        obj = self.api.getOne(objType, id)
        obj.delete()

    @staticmethod
    def name():
        return "delete"

    @staticmethod
    def addArgs(parser):
        parser.add_argument('type')
        parser.add_argument('id')

class SchemaCommand(Command):
    def run(self):
        if self.args.type:
            for attr,meta in self.api.schema(self.args.type)['fields'].iteritems():
                print "%s:"%(attr)
                for name,value in meta.iteritems():
                    print "\t%s: %s"%(name, value)
        else:
            for obj in self.api.schema():
                print obj

    @staticmethod
    def name():
      return "schema"

    @staticmethod
    def addArgs(parser):
        parser.add_argument('type', nargs='?', default=None)

parser = argparse.ArgumentParser()
cli.add_argument_group(parser)

subparsers = parser.add_subparsers(title='commands', description='Valid commands', help='Command')

for cmd in [ListCommand, GetCommand, UpdateCommand, CreateCommand,
    DeleteCommand, SchemaCommand]:
  subparser = subparsers.add_parser(cmd.name())
  cmd.addArgs(subparser)
  subparser.set_defaults(cmd=cmd)

args = parser.parse_args(sys.argv[1:])
api = cli.api_from_args(args)
if api is None:
    print "Could not discover an API."
    sys.exit(1)
cmd = args.cmd(api, args)

cmd.run()
