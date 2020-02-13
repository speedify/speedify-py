import time
import subprocess
import json
import random
import os.path
import logging
from enum import Enum
from sys import platform

# full path to cli exe
global connectifycli
cli = None


def setConnectifyCLI():
        "Finds the path for the CLI, or throws a ConenctifyError"

        # todo: do we need a relative one for development?
        possible_paths = ['c://program files (x86)//connectify//connectify_cli.exe',
                          'c://program files//connectify//connectify_cli.exe',
                          ]
        for pp in possible_paths:
                if os.path.isfile(pp):
                        logging.debug("Using cli of (" + pp + ")")
                        return pp
        raise ConnectifyError("Speedify CLI not found")

## Low level functions for dealing with the CLI
class ConnectifyError(Exception):
    """Base class for exceptions in this module."""
    def __init__(self,  message, errortext=None, errorcode=None):
            self.message = message
            # TODO: method to make error code available as hex
            self.errorcode = errorcode
            self.errortext = errortext

def isConnectifyInstalled():
    try:
        cli = setConnectifyCLI()
        return True;
    except ConnectifyError:
        return False

def runConnectifyCmd(args, target=None):
    "passes list of args to connectify command line returns the objects pulled from the json"
    resultstr = ""
    try:
        global cli
        if cli == None:
            cli = setConnectifyCLI()
        # I'm not escaping stuff, because python is at least wrapping every argument in double quotes automatically.  maybe does everything.
        cmd = [cli] + args
        # I'm not sure how well, if at all, emoji's will work passed through the shell like this.
        # TODO: In other languages, I used the --interactive so that all that stuff went back and GetFolderPath
        # through a pipe i was able to mark as UTF8.
        #logging.debug("Calling cli with " + str(cmd))
        # don't forget to get rid of the timeout if we ever go to --interactive mode
        # TODO: timeout does not work, don't know why
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,check=True,timeout=120)
        resultstr = result.stdout.decode('utf-8').strip()

        jret = json.loads(resultstr)
        # TODO: error if there's no res
        if jret["res"] == False:
            logging.warning("Error running connectify cmd: " + resultstr);
            err = jret["err"];
            # TODO: error if these are missing
            errCode = err["errorCode"];
            errText = err["errorText"]
            logging.info("errText " + errText)
            raise ConnectifyError("ConnectifyError (" + str(errCode) + ") " + str(errText), errCode, errText)
        # now we should really pull out the one json object the user really wanted
        if target is not None:
            # TODO: error if this doesn't exist
            return jret[target]
        else:
            return None
    except subprocess.TimeoutExpired as te:
        logging.warning("Command timed out")
        logging.exception(te);
        raise ConnectifyError("Command timed out: " + args[0])
    except ValueError as err:
        logging.warning ('Error running cmd, bad json: (' + resultstr + ')')
        logging.exception( err)
        raise ConnectifyError("Invalid output from CLI")
    except subprocess.CalledProcessError as cpe:
        logging.warning("CalledProcessError")
        logging.exception( cpe)
        out = cpe.stderr.decode('utf-8')
        if not out:
            out=cpe.stdout.decode('utf-8')
        out = out.strip()
        if(out.startswith("connectify_cli")):
            raise SpeedifyError("Unknown command")
        else:
            logging.warning ("runConnectifyCmd CPE error :" + out)
            raise SpeedifyError("Error: " + out)


# Starts your hotspot
def start(ssid, password, inetMode="routed", inet="bridged"):
    "Starts the hotspot"
    logging.debug("  Starting Hotspot with SSID ="+ssid)
    command = ["start"]
    if (ssid != None) and (ssid != ""):
        command.append("--ssid")
        command.append(ssid)
    if (password != None) and (password != ""):
        command.append("--pass")
        command.append(password)
    if (inetMode != None) and ((inetMode == ("bridged")) or inetMode ==("routed")):
        command.append("--inet-mode")
        command.append(inetMode)
    if (inet != None) and (inet != ""):
        command.append("--inet")
        command.append(inet)
    runConnectifyCmd(command)
    logging.debug("  Started hotspot")

def clients(connected=True, disconnected=True):
    "lists clients"
    command = ["clients"]
    if connected == True and disconnected == False:
        command.append("--connected")
    elif connected == False and disconnected == True:
        command.append("--disconnected")

    return runConnectifyCmd(command, "clients")


def status():
    "Returns connectify status: Enabled, Disabled, etc."
    return runConnectifyCmd(["status"], "status")

def settings():
    "Returns connectify settings"
    return runConnectifyCmd(["settings"], "settings")
def info():
    "Returns kstats about the running hotspot"
    return runConnectifyCmd(["info"], "info")
def listAdapters():
    "List of network adapters"
    return runConnectifyCmd(["list-adapters"], "list-adapters")

def stop():
    "Stops the hotspot"
    logging.debug("Stop hotspot")
    runConnectifyCmd(["stop"])

def version():
    "Returns connectify version"
    return runConnectifyCmd(["version"], "version")