#!/usr/bin/env python3
# coding: utf8

from configparser import ConfigParser
from os import system, name

if name == 'nt':
    _ = system('cls')

else:
    _ = system('clear')

parser = ConfigParser()
parser.read('config.ini')

print("Detected configuration:")

if parser.has_section("OVH"):
    print("  OVH: ")
    if parser.has_option("OVH", "endpoint"):
        print("   -Endpoint: "+parser.get("OVH", "endpoint"))
    else:
        print("   /!\\ Missing endpoint /!\\")

    if parser.has_option("OVH", "application_key"):
        print("   -Application key: "+parser.get("OVH", "application_key"))
    else:
        print("   /!\\ Missing application_key /!\\")

    if parser.has_option("OVH", "application_secret"):
        print("   -Application Secret: "+parser.get("OVH", "application_secret"))
    else:
        print("   /!\\ Missing application_secret /!\\")

    if parser.has_option("OVH", "consumer_key"):
        print("   -Consumer Key: "+parser.get("OVH", "consumer_key"))
    else:
        print("   /!\\ Missing consumer_key /!\\")

    if parser.has_option("OVH", "service_name"):
        print("   -Service Name: "+parser.get("OVH", "service_name"))
    else:
        print("   /!\\ Missing service_name /!\\")
else:
    print("  /!\\ No OVH section /!\\")

print("")

if parser.has_section("MAIL"):
    print("  MAIL: ")
    if parser.has_option("MAIL", "username"):
        print("   -Mail: "+parser.get("MAIL", "username"))
    else:
        print("   /!\\ Missing username /!\\")

    if parser.has_option("MAIL", "password"):
        print("   -Password: "+parser.get("MAIL", "password"))
    else:
        print("   /!\\ Missing password /!\\")

    if parser.has_option("MAIL", "server"):
        print("   -Server: "+parser.get("MAIL", "server"))
    else:
        print("   /!\\ Missing server /!\\")

    if parser.has_option("MAIL", "port"):
        print("   -Port: "+parser.get("MAIL", "port"))
    else:
        print("   /!\\ Missing port /!\\")

    if parser.has_option("MAIL", "receivers"):
        print("   -Receivers: "+str(parser.get("MAIL", "receivers").split(", ")))
    else:
        print("   /!\\ Missing receivers /!\\")
else:
    print("  /!\\ No MAIL section /!\\")



print("")
