#!/usr/bin/python3
# Uses Python 3.7

import json
import logging
import subprocess
import os
from enum import Enum
from functools import wraps

from utils import use_shell
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

"""
.. module:: speedify
   :synopsis: Contains speedify cli wrapper functions
"""

class State(Enum):
    """Enum of speedify states.
    """
    LOGGED_OUT = 0
    LOGGING_IN = 1
    LOGGED_IN = 2
    AUTO_CONNECTING = 3
    CONNECTING = 4
    DISCONNECTING = 5
    CONNECTED = 6
    OVERLIMIT = 7
    UNKNOWN = 8

class Priority(Enum):
    """Enum of speedify connection priorities.
    """
    ALWAYS='always'
    BACKUP='backup'
    SECONDARY='secondary'
    NEVER='never'

class SpeedifyError(Exception):
    """Generic error thrown by library.
    """
    def __init__(self,  message):
        self.message = message

class SpeedifyAPIError(SpeedifyError):
    """Error thrown if speedify gave a bad json response.
    """
    def __init__(self, error_code, error_type, error_message):
        self.error_code = error_code
        self.error_type = error_type
        self.error_message = error_message
        self.message =error_message

_cli_path = None

def set_cli(new_cli_path):
    """Change the path to the cli after importing the module.
    The path defaults to the cli's default install location.

    :param new_cli_path:  Full path to speedify_cli.
    :type new_cli_path: str
    """
    global _cli_path
    _cli_path = new_cli_path

def get_cli():
    '''
    :returns:  str -- The full path to the speedify cli.
    '''
    global _cli_path
    if ((_cli_path == None) or  (_cli_path == "")):
        _cli_path = _find_cli()
    return _cli_path

def find_state_for_string(mystate):
    return State[str(mystate).upper().strip()]

def exception_wrapper(argument):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                result = function(*args, **kwargs)
                return result
            except SpeedifyError as err:
                logger.error(argument + ": " + err.message)
                raise err
        return wrapper
    return decorator

# Functions for controlling Speedify State

@exception_wrapper("Failed to connect")
def connect(server=""):
    '''
    connect(server="")
    Tell Speedify to connect. Returns serverInformation if success, raises Speedify if unsuccessful.
    See show_servers() for the list of servers available.

    :param server: Server to connect to.
    :type server: str
    :returns:  dict -- :ref:`JSON currentserver <connect>` from speedify.
    '''
    args = ['connect']
    if(server!= None and server != ""):
        pieces = server.split("-")
        for piece in pieces:
            args.append(piece)
        logger.debug('connecting to server = ' + server)

    resultjson = _run_speedify_cmd(args)
    return resultjson

def connect_closest():
    '''Connects to the closest server

    :returns:  dict -- :ref:`JSON currentserver <connect>` from speedify.
    '''
    return connect("closest")
def connect_public():
    '''Connects to the closest public server

    :returns:  dict -- :ref:`JSON currentserver <connect>` from speedify.
    '''
    return connect("public")
def connect_private():
    '''Connects to the closest private server

    :returns:  dict -- :ref:`JSON currentserver <connect>` from speedify.
    '''
    return connect("private")
def connect_p2p():
    '''Connects to a server that allows p2p traffic

    :returns:  dict -- :ref:`JSON currentserver <connect>` from speedify.
    '''
    return connect("p2p")
def connect_country(country="us"):
    '''Connects to a server via the 2 letter country code
    See show_servers() for the list of servers available.

    :param country: 2 letter country code.
    :type country: str
    :returns:  dict -- :ref:`JSON currentserver <connect>` from speedify.
    '''
    return connect(country)
def connect_last():
    '''Connects to the last server

    :returns:  dict -- :ref:`JSON currentserver <connect>` from speedify.
    '''
    return connect("last")

@exception_wrapper("Disconnect failed")
def disconnect():
    '''
    disconnect()
    Disconnects. Waits for disconnect to complete

    :returns: bool -- TRUE if disconnect succeeded
    '''
    _run_speedify_cmd(["disconnect"])
    return True

@exception_wrapper("Failed to set connect method")
def connectmethod(method, country="us", city=None, num=None):
    '''
    connectmethod(method, country="us", city=None, num=None)
    Sets the default connectmethod of closest,p2p,private or country (in which case country is required)

    :param method: The connect method.
    :type method: str
    :param country: 2 letter country code.
    :type country: str
    :param city: The (optional) city the server is located.
    :type city: str
    :param num: The (optional) server number.
    :type num: int
    :returns:  dict -- :ref:`JSON connectmethod <connectmethod>` from speedify.
    '''
    args = ['connectmethod']
    if method == "dedicated":
        method = "private"
    if(method == "country"):
        args.append(country)
        if(city != None):
            args.append(city)
            if (num != None):
                args.append(num)
    elif method:
        args.append(method)
    resultjson = _run_speedify_cmd(args)
    return resultjson

def connectmethod_as_string(connectMethodObject, hypens=True):
    ''' takes the JSON returned by show_connectmethod and turns it into a string
    either with -s for places that want us-nova-2 type strings, or with spaces
    for passing to command line of connectmethod, "us nova 2", for example
    '''
    sep = " "
    if hypens:
        sep = "-"
    ret = connectMethodObject["connectMethod"]
    if  ret == "country":
        ret = str(connectMethodObject["country"])
        if connectMethodObject["city"]:
            ret = ret + sep + str(connectMethodObject["city"])
            if connectMethodObject["num"]:
                ret = ret + sep + str(connectMethodObject["num"])
    return ret

@exception_wrapper("Failed to login")
def login(user, password):
    '''
    login(user, password)
    Login.  Returns a State.  returns the state if succesful

    :param user: username
    :type user: str
    :param password: password
    :type password: str
    :returns:  speedify.State -- The speedify state enum.
    '''
    args = ['login', user, password]
    resultjson = _run_speedify_cmd(args)
    return find_state_for_string(resultjson["state"])

@exception_wrapper("Failed to logout")
def logout():
    '''
    logout()
    logout.  returns the state, desc=LOGGED_OUT is a success

    :returns:  speedify.State -- The speedify state enum.
    '''
    jret = _run_speedify_cmd(['logout'])
    return find_state_for_string(jret["state"])

### Getter functions ###

@exception_wrapper("Failed to get server list")
def show_servers():
    '''
    show_servers()
    Returns all the servers, public and private

    :returns:  dict -- :ref:`JSON server list <show-servers>` from speedify.
    '''
    return _run_speedify_cmd(['show', 'servers'])

@exception_wrapper("Failed to get privacy")
def show_privacy():
    '''
    show_privacy()
    Returns privacy settings

    :returns:  dict -- dict -- :ref:`JSON privacy <show-privacy>` from speedify.
    '''
    return _run_speedify_cmd(['show', 'privacy'])

@exception_wrapper("Failed to get settings")
def show_settings():
    '''
    show_settings()
    Returns current settings

    :returns:  dict -- dict -- :ref:`JSON settings <show-settings>` from speedify.
    '''
    return _run_speedify_cmd(['show', 'settings'])

@exception_wrapper("Failed to get adapters")
def show_adapters():
    '''
    show_adapters()
    Returns current adapters

    :returns:  dict -- dict -- :ref:`JSON list of adapters <show-adapters>` from speedify.
    '''
    return _run_speedify_cmd(['show', 'adapters'])

@exception_wrapper("Failed to do captiveportal_check")
def captiveportal_check():
    '''
    captiveportal_check()
    Returns adapters which are currently blocked by a captive portal

    :returns:  dict -- dict -- :ref:`JSON list of adapters behind captive portal` from speedify.
    '''
    return _run_speedify_cmd(['captiveportal', 'check'])

@exception_wrapper("Failed to do captiveportal_login")
def captiveportal_login(proxy=True, adapterID = None):
    '''
    captiveportal_login()
    Starts or stops the local proxy intercepting traffic on ports 52,80,433, for
    filling in a captive portal.   If the user interface is running, once this is
    turned on, it will launch a captive portal browser.  If it's not, then it's
    up to you to launch a browser pointing at an http website to get to the
    portal page.

    :param proxy: Whether the local proxy should intercept captive portal traffic
    :type priority: boolean
    :param adapterID: The interface adapterID
    :type adapterID: str

    :returns:  dict -- dict -- :ref:`JSON list of adapters behind captive portal` from speedify.
    '''
    args = ['captiveportal', 'login']
    startproxy = True
    if proxy == "on":
        args.append("on")
    elif proxy == "off":
        startproxy = False
        args.append("off")
    elif proxy:
        args.append("on")
    else:
        startproxy = False
        args.append("off")


    if adapterID and startproxy:
        args.append(adapterID)
    return _run_speedify_cmd(args)

@exception_wrapper("Failed to get current server")
def show_currentserver():
    '''
    show_currentserver()
    Returns current server

    :returns:  dict -- :ref:`JSON currentserver <show-currentserver>` from speedify.
    '''
    return _run_speedify_cmd(['show', 'currentserver'])

@exception_wrapper("Failed to get current user")
def show_user():
    '''
    show_user()
    Returns current user

    :returns:  dict -- :ref:`JSON response <show-user>` from speedify.
    '''
    return _run_speedify_cmd(['show', 'user'])

@exception_wrapper("Failed to show connect method")
def show_connectmethod():
    '''
    show_connectmethod()
    Returns the connectmethod related settings

    :returns:  :ref:`JSON response <show-connectmethod>` from speedify.
    '''
    return _run_speedify_cmd(['show', 'connectmethod'])

@exception_wrapper("getting state")
def show_state():
    '''
    show_state()
    Returns the current state of Speedify (CONNECTED, CONNECTING, etc.)

    :returns:  speedify.State -- The speedify state enum.
    '''
    jret = _run_speedify_cmd(['state'])
    return find_state_for_string(jret["state"])

@exception_wrapper("Failed to get version")
def show_version():
    '''
    show_version()
    Returns speedify version

    :returns:  dict -- :ref:`JSON version <version>` from speedify.
    '''
    return  _run_speedify_cmd(['version'])

### Setter functions ###
@exception_wrapper("Failed to set adapter priority")
def adapter_priority(adapterID, priority=Priority.ALWAYS):
    '''
    adapter_priority(adapterID, priority=Priority.ALWAYS)
    Sets the priority on the adapter whose adapterID is provided (show_adapters is where you find the adapterIDs)

    :param adapterID: The interface adapterID
    :type adapterID: str
    :param priority: The speedify priority
    :type priority: speedify.Priority
    :returns:  dict -- :ref:`JSON adapter response <adapter-ratelimit>` from speedify.
    '''
    args = ['adapter',"priority"]
    args.append(str(adapterID))
    args.append((str(priority.value)))
    resultjson = _run_speedify_cmd(args)
    return resultjson

@exception_wrapper("Failed to set adapter encryption")
def adapter_encryption(adapterID, encrypt):
    '''
    adapter_encryption(adapterID, encrypt)
    Sets the encryption on the adapter whose adapterID is provided (show_adapters is where you find the adapterIDs).

    Note that any time the main encryption() function is called, all the per adapter encryption settings are immeidately reset.

    :param adapterID: The interface adapterID
    :type adapterID: str
    :param priority: Whether to encrypt
    :type encrypt: boolean
    :returns:  dict -- :ref:`JSON adapter response <adapter-encryption>` from speedify.
    '''
    args = ['adapter',"encryption"]
    args.append(str(adapterID))
    if encrypt == "on":
        args.append("on")
    elif encrypt == "off":
        args.append("off")
    elif encrypt:
        args.append("on")
    else:
        args.append("off")
    resultjson = _run_speedify_cmd(args)
    return resultjson

@exception_wrapper("Failed to set adapter ratelimit")
def adapter_ratelimit(adapterID, ratelimit=0):
    '''
    adapter_ratelimit(adapterID, ratelimit=0)
    Sets the ratelimit in bps on the adapter whose adapterID is provided
    (show_adapters is where you find the adapterIDs)

    :param adapterID: The interface adapterID
    :type adapterID: str
    :param ratelimit: The ratelimit in bps
    :type ratelimit: int
    :returns:  dict -- :ref:`JSON adapter response <adapter-datalimit-daily>` from speedify.
    '''
    args = ['adapter',"ratelimit"]
    args.append(str(adapterID))
    args.append((str(ratelimit)))
    resultjson = _run_speedify_cmd(args)
    return resultjson

@exception_wrapper("Failed to set adapter daily limit")
def adapter_datalimit_daily( adapterID, limit=0):
    '''
    adapter_datalimit_daily( adapterID, limit=0)
    Sets the daily usage limit in bytes on the adapter whose adapterID is provided
    (show_adapters is where you find the adapterIDs)

    :param adapterID: The interface adapterID
    :type adapterID: str
    :param limit: The daily usage limit, in bytes
    :type limit: int
    :returns:  dict -- :ref:`JSON adapter response <adapter-datalimit-daily>` from speedify
    '''
    args = ['adapter',"datalimit", "daily"]
    args.append(str(adapterID))
    args.append((str(limit)))
    resultjson = _run_speedify_cmd(args)
    return resultjson

@exception_wrapper("Failed to set adapter monthly limit")
def adapter_datalimit_monthly(adapterID, limit=0, reset_day=0):
    '''
    adapter_datalimit_monthly(adapterID, limit=0, reset_day=0)
    Sets the monthly usage limit in bytes on the adapter whose adapterID is provided
    (show_adapters is where you find the adapterIDs)

    :param adapterID: The interface adapterID
    :type adapterID: str
    :param limit: The monthly usage limit, in bytes
    :type limit: int
    :param reset_day: The day of the month to reset monthly usage (0-31)
    :type reset_Day: int
    :returns:  dict -- :ref:`JSON adapter response <adapter-datalimit-monthly>` from speedify.
    '''
    args = ['adapter', "datalimit", "monthly"]
    args.append(str(adapterID))
    args.append((str(limit)))
    args.append(str(reset_day))

    resultjson = _run_speedify_cmd(args)
    return resultjson

@exception_wrapper("Failed to reset adapter usage")
def adapter_resetusage(adapterID):
    '''
    adapter_resetusage(adapterID)
    Resets all the stats on this adapter back to 0.  Starts both daily and monthly limits over, if set.

    :param adapterID: The interface adapterID
    :type adapterID: str
    :returns:  dict -- :ref:`JSON adapter response <adapter-resetusage>` from speedify.
    '''
    args = ['adapter', "resetusage"]
    args.append(str(adapterID))

    resultjson = _run_speedify_cmd(args)
    return resultjson

@exception_wrapper("Failed to set ports")
def ports(tcpports=[], udpports=[]):
    '''
    ports(tcpports=[], udpports=[])
    sets port forwarding. call with no arguments to unset all port forwarding

    :param tcpports: List of tcp ports to forward on
    :type tcpport: list
    :param udpports: List of udp ports to forward on
    :type udpport: list
    :returns:  dict -- :ref:`JSON settings <ports>` from speedify
    '''
    args = ['ports']
    if tcpports is not None:
        for port in tcpports:
            args.append(str(port) + "/tcp")
    if udpports is not None:
        for port in udpports:
            args.append(str(port) + "/udp")

    resultjson = _run_speedify_cmd(args)
    return resultjson

@exception_wrapper("Failed to change modes")
def mode(mode="speed"):
    '''
    mode(mode="speed")
    Set 'redundant' or 'speed' operation modes

    :param mode: "redundant" or "speed"
    :type mode: str
    :returns:  dict -- :ref:`JSON settings <mode>` from speedify
    '''
    args = ['mode',mode]
    resultjson = _run_speedify_cmd(args)
    return resultjson

@exception_wrapper("Failed to set encryption")
def encryption(encrypt=True):
    '''
    encryption(encrypt=True)
    Sets encryption on or off.

    :param encrypt: Encrypted on or off
    :type encrypt: bool
    :returns:  dict -- :ref:`JSON settings <encryption>` from speedify
    '''
    args = ['encryption']
    if encrypt == "on":
        args.append("on")
    elif encrypt == "off":
        args.append("off")
    elif encrypt:
        args.append("on")
    else:
        args.append("off")
    resultjson = _run_speedify_cmd(args)
    return resultjson

@exception_wrapper("Failed to set jumbo")
def jumbo(mode=True):
    '''
    jumbo(mode=True)
    Sets jumbo MTU mode on or off.

    :param mode: Jumbo MTU on or off
    :type mode: bool
    :returns:  dict -- :ref:`JSON settings <jumbo>` from speedify
    '''
    args = ['jumbo']
    if mode == "on":
        args.append("on")
    elif mode == "off":
        args.append("off")
    elif mode == True:
        args.append("on")
    elif mode == False:
        args.append("off")
    else:
        #probably invalid, but we'll let speedify tell us THAT
        args.append(mode)

    resultjson = _run_speedify_cmd(args)
    return resultjson

@exception_wrapper("Failed to set packetaggregation")
def packetaggregation(mode=True):
    '''
    packetaggregation(mode=True)
    Sets packetaggregation mode on or off.

    :param mode: packetaggregation on or off
    :type mode: bool
    :returns:  dict -- :ref:`JSON settings <packetaggr>` from speedify
    '''
    args = ['packetaggr']
    if mode == "on":
        args.append("on")
    elif mode == "off":
        args.append("off")
    elif mode == True:
        args.append("on")
    elif mode == False:
        args.append("off")
    else:
        #probably invalid, but we'll let speedify tell us THAT
        args.append(mode)

    resultjson = _run_speedify_cmd(args)
    return resultjson

@exception_wrapper("Failed to set killswitch")
def killswitch(killswitch=False):
    '''
    killswitch(killswitch=False)
    sets killswitch on or off. (Windows only)

    :param killswitch: killswitch on or off
    :type killswitch: bool
    :returns:  dict -- :ref:`JSON privacy response <privacy-killswitch>` from speedify
    '''
    args = ['privacy','killswitch']
    args.append("on") if killswitch else args.append("off")
    resultjson = _run_speedify_cmd(args)
    return resultjson

@exception_wrapper("Failed to set overflow")
def overflow(speed_in_mbps=30.0):
    '''
    overflow(speed_in_mbps=30.0)
    sets overflow threshold.

    :param speed_in_mbps: Overflow threshold in mbps
    :type speed_in_mbps: float
    :returns:  dict -- :ref:`JSON settings <overflow>` from speedify
    '''
    args = ['overflow']
    args.append(str(speed_in_mbps))
    resultjson = _run_speedify_cmd(args)
    return resultjson

@exception_wrapper("Failed to set dnsleak")
def dnsleak(leak=False):
    '''
    dnsleak(leak=False)
    sets dnsleak on or off. (Windows only)

    :param dnsleak: dnsleak on or off
    :type dnsleak: bool
    :returns:  dict -- :ref:`JSON privacy response <privacy-dnsleak>` from speedify
    '''
    args = ['privacy','dnsleak']
    args.append("on") if leak else args.append("off")
    resultjson = _run_speedify_cmd(args)
    return resultjson

@exception_wrapper("Failed to set crashreports")
def crashreports(report=True):
    '''
    crashreports(report=True)
    sets crashreports on or off.

    :param report: crashreports on or off
    :type dnsleak: bool
    :returns:  dict -- :ref:`JSON privacy response <privacy-crashreports>` from speedify
    '''
    args = ['privacy','crashreports']
    args.append("on") if report else args.append("off")
    resultjson = _run_speedify_cmd(args)
    return resultjson

@exception_wrapper("Failed to set startupconnect")
def startupconnect(connect=True):
    '''
    startupconnect(connect=True)
    sets whether to automatically connect on login.

    :param connect: Sets connect on startup on/off
    :type connect: bool
    :returns:  dict -- :ref:`JSON settings <startupconnect>` from speedify
    '''
    args = ['startupconnect']
    args.append("on") if connect else args.append("off")
    resultjson = _run_speedify_cmd(args)
    return resultjson

@exception_wrapper("Failed to set routedefault")
def routedefault(route=True):
    '''
    routedefault(route=True)
    sets whether Speedify should take the default route to the internet.
    defaults to True, only make it False if you're planning to set up
    routing rules, like IP Tables, yourself..

    :param connect: Sets routedefault on/off
    :type connect: bool
    :returns:  dict -- :ref:`JSON settings <routedefault>` from speedify
    '''
    args = ['route','default']
    args.append("on") if route else args.append("off")
    resultjson = _run_speedify_cmd(args)
    return resultjson

@exception_wrapper("Failed to run speedtest")
def speedtest():
    '''
    speedtest()
    Returns runs speed test returns final results. Will take around 30 seconds.

    :returns:  dict -- :ref:`JSON speedtest <speedtest>` from speedify
    '''
    jret = _run_speedify_cmd(['speedtest'], cmdtimeout=600)
    return jret

@exception_wrapper("Failed to set transport")
def transport(transport='auto'):
    '''
    transport(transport='auto')
    Sets the transport mode (auto/tcp/udp/https).

    :param transport: Sets the transport to "auto","udp","tcp" or "https"
    :type transport: str
    :returns:  dict -- :ref:`JSON settings <transport>` from speedify
    '''
    args = ['transport',transport]
    resultjson = _run_speedify_cmd(args)
    return resultjson

@exception_wrapper("Failed getting stats")
def stats(time=1):
    '''
    stats(time=1)
    calls stats returns a list of all the parsed json objects it gets back

    :param time: How long to run the stats command.
    :type time: int
    :returns:  list -- list JSON stat responses from speedify.
    '''
    if time == 0:
        logger.error('stats cannot be run with 0, would never return')
        raise SpeedifyError("Stats cannot be run with 0")
    if time == 1:
        # fix for bug where passing in 1 returns nothing.
        time = 2
    class list_callback():
        def __init__( self ):
            self.result_list= list()
        def __call__(self, input):
            self.result_list.append(input)

    list_callback = list_callback()
    stats_callback(time, list_callback)
    return list_callback.result_list

def stats_callback(time, callback):
    '''
    stats_callback(time, callback)
    calls stats, and callback supplied function with each line of output. 0 is forever

    :param time: How long to run the stats command.
    :type time: int
    :param callback: Callback function
    :type callback: function
    '''
    args = ["stats", str(time)]
    cmd = [get_cli()] + args

    _run_long_command(cmd, callback)

### Internal functions ###
def _run_speedify_cmd(args, cmdtimeout=60):
    "passes list of args to speedify command line returns the objects pulled from the json"
    resultstr = ""
    try:
        cmd = [get_cli()] + args
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                shell=use_shell(),check=True, timeout=cmdtimeout)
        resultstr = result.stdout.decode('utf-8').strip()
        sep = os.linesep*2
        records = resultstr.split(sep)
        reclen = len(records)
        if reclen > 0:
            return json.loads(records[-1])
        logger.error("command " + args[0] + " had NO records")
        raise SpeedifyError("No output from command " + args[0])
    except subprocess.TimeoutExpired:
        logger.error("Command timed out")
        raise SpeedifyError("Command timed out: " + args[0])
    except ValueError:
        logger.error('Running cmd, bad json: (' + resultstr + ')')
        raise SpeedifyError("Invalid output from CLI")
    except subprocess.CalledProcessError as cpe:
        #TODO: errors can be json now
        out = cpe.stderr.decode('utf-8').strip()
        if not out:
            out=cpe.stdout.decode('utf-8').strip()
        returncode = cpe.returncode
        errorKind = "Unknown"
        if returncode == 1:
            errorKind ="Speedify API"
        elif returncode == 2:
            errorKind = "Invalid Parameter"
        elif returncode == 3:
            errorKind = "Missing Parameter"
        elif returncode == 4:
            errorKind = "Unknown Parameter"
            # whole usage message here, no help
            raise SpeedifyError(errorKind)

        newerror = None
        if (returncode ==1):
            try:
                job = json.loads(out)
                if("errorCode" in job):
                    #json error! came from the speedify daemon
                    newerror = SpeedifyAPIError(job["errorCode"], job["errorType"], job["errorMessage"])
            except ValueError:
                logger.error("Could not parse Speedify API Error: " + out)
                newerror = SpeedifyError(errorKind + ": Could not parse error message")
        else:
            lastline = [ i for i in out.split("\n") if i][-1]
            if lastline:
                newerror = SpeedifyError( str(lastline))
            else:
                newerror = SpeedifyError(errorKind + ": " + str("Unknown error"))

        if newerror:
            raise newerror
        else:
            # treat the plain text as an error, common for valid command, with invalud arguments
            logger.error("runSpeedifyCmd CPE : " + out)
            raise SpeedifyError(errorKind + ": " + str(": " + out))

# CALLBACK VERSIONS
# The normal _run_speedify_cmd runs the command and waits for the final output.
# these versions keep running, calling you back as json objects are emitted. useful
# for stats and for a verbose speedtest, otherwise, stick with the non-callback versions
@exception_wrapper("SpeedifyError in longRunCommand")
def _run_long_command(cmdarray, callback):
    "callback is a function you provide, passed parsed json objects"
    outputbuffer = ""

    with subprocess.Popen(cmdarray, stdout=subprocess.PIPE) as proc:
        for line in proc.stdout:
            line = line.decode('utf-8').strip()
            if line :
                outputbuffer+=(str(line))
            else:
                if outputbuffer:
                    _do_callback(callback,outputbuffer)
                    outputbuffer = ""
                else:
                    outputbuffer = ""

    if outputbuffer:
        _do_callback(callback,outputbuffer)

def _do_callback(callback, message):
    "parsing string as json, calls callback function with result"
    jsonret = ""
    try:
        if message:
            jsonret = json.loads(message)
    except SpeedifyError as e:
        logger.debug("problem parsing json: " + str(e))
    if jsonret:
        try:
            callback(jsonret)
        except SpeedifyError as e:
            logger.warning("problem callback: " + str(e))

# Default cli search locations
def _find_cli():
    '''Finds the path for the CLI'''
    if 'SPEEDIFY_CLI' in os.environ :
        possible = (os.environ['SPEEDIFY_CLI'])
        if possible:
            if os.path.isfile(possible):
                    logging.debug("Using cli from SPEEDIFY_CLI of (" + possible + ")")
                    return possible
            else:
                logging.warning("SPEEDIFY_CLI specified a nonexistant path to cli: \"" +possible + "\"")
    possible_paths = ["/Applications/Speedify.app/Contents/Resources/speedify_cli",
                      'c://program files (x86)//speedify//speedify_cli.exe',
                      'c://program files//speedify//speedify_cli.exe',
                      "/usr/share/speedify/speedify_cli"]
    for pp in possible_paths:
            if os.path.isfile(pp):
                    logging.debug("Using cli of (" + pp + ")")
                    return pp

    logging.error("Could not find speedify_cli!")
    raise SpeedifyError("Speedify CLI not found")
