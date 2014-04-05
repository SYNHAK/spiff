import argparse
import os
from spiff import API
from getpass import getpass
import spaceapi
import logging

def add_argument_group(parser):
    group = parser.add_argument_group('spiff')
    group.add_argument('-u', '--uri', default=None, help="API URL")
    group.add_argument('-d', '--debug', action='store_true', default=False,
        help='Print debugging information')
    group.add_argument('-V', '--no-verify', action='store_false', default=True,
        dest='verify', help='Do not verify the SSL certificate')
    group.add_argument('-A', '--anonymous', action='store_true', default=False,
        help="Do not ask for a login")
    return group

def api_from_argv(argv=None, parser=None):
    if parser is None:
        parser = argparse.ArgumentParser()
    add_argument_group(parser)
    args = parser.parse_args(argv)
    return (api_from_args(args), args)

def api_from_args(args):
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)
    try:
        api = API.getDefaultAPI(args.uri, args.verify)
    except spaceapi.DiscoveryError:
        return None
    if not args.anonymous:
        login_api(api)
    return api

def login_api(api):
    if 'SPIFF_USERNAME' in os.environ:
        username = os.environ['SPIFF_USERNAME']
    else:
        username = raw_input('Username: ')
    api.login(username, getpass())
