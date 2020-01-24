import subprocess

import speedify
from speedify import State
from utils import use_shell
import platform
import logging

def confirm_state_speedify(state = State.LOGGED_IN):
    "Confirms with a True|False whether speedify is in state you pass in"
    desc = speedify.show_state()
    if state == desc:
        return True
    else:
        logging.error ("confirmStateSpeedify Failed command results: "+ str(desc))
        return False

def list_servers_speedify(public=True, private=False,excludeTest=True):
    "Returns flattened array of servers, excludes any with test in name"
    try:
        serverlist =[]
        jret = speedify.show_servers();
        if public:
            if "public"in jret:
                for server in jret["public"]:
                    serverlist.append(server["tag"])

        if private:
            if "private"in jret:
                for server in jret["private"]:
                    serverlist.append(server["tag"])
        if excludeTest:
            # servers with "test"in the name are bad news
            serverlist2 = [ x for x in serverlist if "-test"not in x ]
            serverlist = serverlist2
        return serverlist
    except speedify.SpeedifyError as err:
         logging.error ('Failed to get server list: ' + err.message)
         return "ERROR"

def using_speedify(destination="8.8.8.8"):
    "Checks that the internet gateway really is a speed server"
    tracert = ["traceroute",'-m', '2',destination]
    if platform.system() == "Windows":
        tracert = ["tracert",'-h', '1','-d',destination]
    elif platform.system() == "Linux":
        tracert = ["mtr",'-m', '2', '-c', '2', '--report', destination]
    try:
        result = subprocess.run(tracert, stdout=subprocess.PIPE, shell=use_shell())
    except FileNotFoundError as e:
        logging.error(e)
        raise e
    resultstr = result.stdout.decode('utf-8')
    if '10.202.0.1' in resultstr:
        return True
    else:
        # print(resultstr)
        return False
