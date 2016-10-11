# Copyright (c) 2016 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
"""This is a sample EapiClient library.  The goal here is to demonstrate
several different approaches to solving the same problem.  I hope that by
doing this the reader will better understand the underlying components and
Python in general.

Concepts Introduced:

    * command-line parsing
    * use of: __name__ == "__main__"
    * formatting strings
    * using various http libraries
    * python objects and classes
    * extending classes and overriding methods
    * hiding private methods
    * 'CONSTANTS' by convention still mutable
"""

# parse command line arguments... makes you look like you know what your doing.
import argparse

# use this library to render or parse JSON data structures
import json

# for demo purposes.  print text in a readable format
import pprint

# using sys for reading stdin
import sys

# really only need one of these... but we are demonstrating various methods
import urllib2
import requests
import jsonrpclib
import pyeapi

# Python metadata
__author__ = "Jesse Mather"
__copyright__ = "Copyright 2016, Arista Networks, Inc."
__credits__ = ["Jesse Mather", "eosplus-dev"]
__license__ = "MIT"
__version__ = "0.1.0"
__version_info__ = (0, 1, 0)
__maintainer__ = "Jesse Mather"
__email__ = "jmather@arista.com"
__status__ = "Alpha"

# Global variables.  By convention in Python ALL_CAPS are constants, but beware
# they are not really constants and can be changed (they are mutable)
JSONRPC_VERSION = "2.0"
JSONRPC_METHOD = "runCmds"
EAPI_VERSION = 1
EAPI_CLIENT_ID = "AristaProgrammability-1"

HTTP_HEADERS = {'Content-Type': 'application/json'}

def client_factory(approach="requests"):


    # a bit of trickery to get the class from its name
    klass = approach.capitalize() + "EapiClient"

    # search through items in current scope for the class name
    get_class = lambda name: globals()[name]

    # return the class itself uninitialized
    return get_class(klass)

def create_jsonrpc_payload(commands, format="json", timestamps=False,
                           auto_complete=False, expand_aliases=False,
                           version=None):
    """
    This function builds python dictionary that can be easily converted to a
    JSONRPC payload.

    Example JSON payload for eAPI requests:

    {
      "jsonrpc": "2.0",
      "method": "runCmds",
      "params": {
        "format": "json",
        "timestamps": false,
        "autoComplete": false,
        "expandAliases": false,
        "cmds": ["show version"],
        "version": 1
      },
      "id": "EapiExplorer-1"
    }
    """

    # If the user does not specify a version, use the global variable. We could
    # just hard code, but that's bad form.
    if not version:
        version = EAPI_VERSION

    params = {
        # format: output to 'json' and 'text' are supported. text
        # output will look just like the CLI and somethings is required if the
        # command has not yet been converted
        # Ex.
        #   "show clock" w/ json format
        #
        # {
        #   "jsonrpc": "2.0",
        #   "id": "EapiExplorer-1",
        #   "error": {
        #     "data": [
        #       {
        #         "errors": [
        #           "Command cannot be used over the API at this time. To see
        #            ASCII output, set format='text' in your request"
        #         ]
        #       }
        #     ],
        #     "message": "CLI command 1 of 1 'show clock' failed: unconverted
        #                 command",
        #     "code": 1003
        #   }
        # }
        #
        # Now with "text" formatting:
        # {
        #   "jsonrpc": "2.0",
        #   "result": [
        #     {
        #       "output": "Tue Oct 11 11:39:37 2016\nTimezone:
        #                  UTC\nClock source: local\n"
        #     }
        #   ],
        #   "id": "EapiExplorer-1"
        # }
        "format": format,
        # timestamps: adds a _meta item to the result:
        # Ex.
        #   "_meta": {
        #     "execDuration": 0.0026209354400634766,
        #     "execStartTime": 1476185494.32511
        #   },
        "timestamps": timestamps,
        # autoComplete: allow partial commands within eAPI. Don't do this. Be
        #               specific.
        # ex. 'sh ip int'
        "autoComplete": auto_complete,
        # expandAliases: Allow calling used defined command aliases
        # ex.
        #  switch(config)#alias ship show ip interfaces
        #   ...and now this works:
        #  commands = ["ship"]
        "expandAliases": expand_aliases,
        # cmds: list of command strings or dictionary objects.
        # more advanced commands can be revisioned or respond to prompts:
        #  ex. commands = [{"cmd": "enable", "input": "s3cr3t"},
        #                  "show running-config"]
        "cmds": commands,
        # version: should be 1 by default
        "version": version,
    }

    # the params from above are embedded inside the top-level payload dictionary
    payload = {
        "jsonrpc": JSONRPC_VERSION,
        "method": JSONRPC_METHOD,
        "params": params,
        "id": EAPI_CLIENT_ID
    }

    return payload

class BaseEapiClient(object):

    def __init__(self, switch_addr, creds=("admin", ""), **kwargs):
        """Constructor for base class. Does not need to be overrided, but it
        can be if more options are needed.  I typical will just add used defined
        initializer if that is needed.  In this case `kwargs` is passed through.
        """

        self.switch_addr = switch_addr
        self.creds = creds

        self._on_init(**kwargs)

    def _on_init(self, **kwargs):
        """Call this method after __init__ is called. i.e. when a new object is
        created. If not overridden, it does nothing. The purpose of the '_'
        is to signify that this method is 'private' or 'internal'.

        Note: Python does NOT enforce 'private' or 'protected' methods.
        """
        return

    def send(self, commands, **kwargs):
        """This is an unimplemented method that is intended to be overridden.
        There is a newer (more enforcing) way to do this by using
        'Abstract Base Classes' and decorators but that sounds scary.  So maybe
        next time.

        Nevermind here's an example:

            import abc

            class BaseEapiClient(object):
                __metaclass__ = abc.ABCMeta

                @abc.abstractmethod
                def send(self, commands, **kwargs):
                    return

        """
        raise NotImplementedError("send must be overridden")

#############################
# Below are a few extensions of the BaseEapiClient class.  Each of them
# operate independently.
#############################

class Urllib2EapiClient(BaseEapiClient):
    """Batteries included, but yucky."""

    def send(self, commands, **kwargs):
        endpoint ="http://{}/command-api".format(self.switch_addr)
        payload = create_jsonrpc_payload(commands, **kwargs)

        username, password = self.creds

        req = urllib2.Request(endpoint)
        # {'Content-Type': 'application/json'}
        req.add_header("Content-Type", HTTP_HEADERS["Content-Type"])
        password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, endpoint, username, password)

        auth_manager = urllib2.HTTPBasicAuthHandler(password_manager)
        opener = urllib2.build_opener(auth_manager)

        urllib2.install_opener(opener)

        handler = urllib2.urlopen(req, data=json.dumps(payload))

        return json.load(handler)["result"]

class RequestsEapiClient(BaseEapiClient):
    """Use the awesome `requests` module to send commands."""

    def send(self, commands, **kwargs):
        endpoint ="http://{}/command-api".format(self.switch_addr)
        payload = create_jsonrpc_payload(commands, **kwargs)

        response = requests.post(endpoint, auth=self.creds,
                                 headers=HTTP_HEADERS,
                                 data=json.dumps(payload),
                                 verify=False)

        # requests does not raise an exception by default
        response.raise_for_status()

        return response.json()["result"]

class JsonrpclibEapiClient(BaseEapiClient):
    """Simple client based in jsonrpclib, but it has terrible documentation :(
    """

    def send(self, commands, **kwargs):
        username, password = self.creds
        url = "http://{}:{}@{}/command-api".format(username, password,
                                                   self.switch_addr)
        conn = jsonrpclib.Server(url)
        return conn.runCmds(1, commands)[0]

# class PyeapiClient(BaseEapiClient):
#     """Arsta's Eos-plus team wrapper eAPI calls.  Can use a config file to
#     simplify command line arguments or support switches with varying creds
#     or transports"""
#
#     def _on_init(self, **kwargs):
#         """overriding _on_init to load the config file"""
#         self.config_file = kwargs.get("config_file", None)
#
#     def send(self, commands, **kwargs):
#         pass

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(prog="arcomm")
    arg = parser.add_argument

    arg("switches", nargs="*")

    arg("-v", "--version", action="store_true", help="display version info")

    arg("--encoding", default="text", choices=["json", "text"],
        help="control output formatting")

    arg("-a", "--approach",
        default="requests",
        choices=["urllib2", "requests", "jsonrpclib"] #, "pyeapi"],
        help="choose which libraries to use for this request")

    arg("-u", "--username", default="admin",
        help="specifies the username on the switch")

    arg("-p", "--password", default="", help="specifies users password")

    args = parser.parse_args()

    if args.version:
        parser.exit(0, __version__ + "\n")

    commands = []
    creds = (args.username, args.password)

    approach = args.approach

    encoding = args.encoding

    for line in sys.stdin:
        commands.append(line.strip())

    for switch in args.switches:
        adapter_class = client_factory(approach)
        client = adapter_class(switch, creds=creds)

        response = client.send(commands)

        print "HOST:", switch
        print "APPROACH:", approach.capitalize()
        print "RESPONSE:"
        pprint.pprint(response)

if __name__ == "__main__":
    main()
