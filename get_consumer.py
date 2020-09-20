#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import ovh
from configparser import ConfigParser

parser = ConfigParser()
parser.read('config.ini')

if parser.has_section("OVH"):
    if parser.has_option("OVH", "endpoint"):
        ovh_endpoint = parser.get("OVH", "endpoint")
    else:
        print("   /!\\ Missing OVH::endpoint in config /!\\")
        exit()

    if parser.has_option("OVH", "application_key"):
        ovh_application_key = parser.get("OVH", "application_key")
    else:
        print("   /!\\ Missing OVH::application_key in config /!\\")
        exit()

    if parser.has_option("OVH", "application_secret"):
        ovh_application_secret = parser.get("OVH", "application_secret")
    else:
        print("   /!\\ Missing OVH::application_secret in config /!\\")
        exit()


client = ovh.Client(
    endpoint = ovh_endpoint,
    application_key = ovh_application_key,
    application_secret = ovh_application_secret,
)

ck = client.new_consumer_key_request()
ck.add_rules(ovh.API_READ_ONLY, "/me")

validation = ck.request()

print("Welcome", client.get('/me')['firstname'])
print("Your 'consumerKey' is '%s'" % validation['consumerKey'])
print("Please visit %s to enable it" % validation['validationUrl'])
print("")
print("You can read the doc at https://github.com/ovh/python-ovh")
