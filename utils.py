#!/usr/bin/python3
# Uses Python 3.7
import logging
import platform
import socket

#Fastest answer from https://stackoverflow.com/questions/3764291/checking-network-connection
def ping_internet(host="8.8.8.8", port=53, timeout=3):
   """
   Host: 8.8.8.8 (google-public-dns-a.google.com)
   OpenPort: 53/tcp
   Service: domain (DNS/TCP)
   """
   try:
       socket.setdefaulttimeout(timeout)
       socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
       return True
   except socket.error as ex:
       logging.warning(ex.message)
       return False

def use_shell():

    if platform.system().lower() == "darwin":
        return False
    if platform.system().lower() == "linux":
        return False
    else:
        return True
