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
    """Enum of speedify states."""

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
    """Enum of speedify connection priorities."""

    ALWAYS = "always"
    BACKUP = "backup"
    SECONDARY = "secondary"
    NEVER = "never"


class SpeedifyError(Exception):
    """Generic error thrown by library."""

    def __init__(self, message):
        self.message = message


class SpeedifyAPIError(SpeedifyError):
    """Error thrown if speedify gave a bad json response."""

    def __init__(self, error_code, error_type, error_message):
        self.error_code = error_code
        self.error_type = error_type
        self.error_message = error_message
        self.message = error_message


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
    """
    :returns:  str -- The full path to the speedify cli.
    """
    global _cli_path
    if (_cli_path == None) or (_cli_path == ""):
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
def connect(server: str = ""):
    """
    connect(server="")
    Tell Speedify to connect. Returns serverInformation if success, raises Speedify if unsuccessful.
    See show_servers() for the list of servers available.

    Example:
        connect()
        connect("us nyc 11") # server numbers may change, use show_servers()

    :param server: Server to connect to.
    :type server: str
    :returns:  dict -- :ref:`JSON currentserver <connect>` from speedify.
    """
    args = ["connect"] + server.split()
    return _run_speedify_cmd(args)


def connect_closest():
    """Connects to the closest server

    :returns:  dict -- :ref:`JSON currentserver <connect>` from speedify.
    """
    return connect("closest")


def connect_public():
    """Connects to the closest public server

    :returns:  dict -- :ref:`JSON currentserver <connect>` from speedify.
    """
    return connect("public")


def connect_private():
    """Connects to the closest private server

    :returns:  dict -- :ref:`JSON currentserver <connect>` from speedify.
    """
    return connect("private")


def connect_p2p():
    """Connects to a server that allows p2p traffic

    :returns:  dict -- :ref:`JSON currentserver <connect>` from speedify.
    """
    return connect("p2p")


def connect_country(country: str = "us"):
    """Connects to a server via the 2 letter country code
    See show_servers() for the list of servers available.

    :param country: 2 letter country code.
    :type country: str
    :returns:  dict -- :ref:`JSON currentserver <connect>` from speedify.
    """
    return connect(country)


def connect_last():
    """Connects to the last server

    :returns:  dict -- :ref:`JSON currentserver <connect>` from speedify.
    """
    return connect("last")


@exception_wrapper("Disconnect failed")
def disconnect():
    """
    disconnect()
    Disconnects. Waits for disconnect to complete

    :returns: bool -- TRUE if disconnect succeeded
    """
    _run_speedify_cmd(["disconnect"])
    return True


@exception_wrapper("Failed to set connect method")
def connectmethod(method, country="us", city=None, num=None):
    """
    connectmethod(method, country="us", city=None, num=None)
    Sets the default connectmethod of --
        closest
        public
        private
        p2p
        country (in which case country is required)

    :param method: The connect method.
    :type method: str
    :param country: 2 letter country code.
    :type country: str
    :param city: The (optional) city the server is located.
    :type city: str
    :param num: The (optional) server number.
    :type num: int
    :returns:  dict -- :ref:`JSON connectmethod <connectmethod>` from speedify.
    """
    args = ["connectmethod"]
    if method == "dedicated":
        method = "private"
    if method == "country":
        args.append(country)
        if city != None:
            args.append(city)
            if num != None:
                args.append(num)
    elif method:
        args.append(method)
    resultjson = _run_speedify_cmd(args)
    return resultjson


def connectmethod_as_string(connectMethodObject, hypens=True):
    """takes the JSON returned by show_connectmethod and turns it into a string
    either with -s for places that want us-nova-2 type strings, or with spaces
    for passing to command line of connectmethod, "us nova 2", for example
    """
    sep = " "
    if hypens:
        sep = "-"
    ret = connectMethodObject["connectMethod"]
    if ret == "country":
        ret = str(connectMethodObject["country"])
        if connectMethodObject["city"]:
            ret = ret + sep + str(connectMethodObject["city"])
            if connectMethodObject["num"]:
                ret = ret + sep + str(connectMethodObject["num"])
    return ret


@exception_wrapper("Failed to login")
def login(user, password):
    """
    login(user, password)
    Login. Returns a State. State object will hold
    information on the success of this command.

    :param user: username
    :type user: str
    :param password: password
    :type password: str
    :returns:  speedify.State -- The speedify state enum.
    """
    args = ["login", user, password]
    resultjson = _run_speedify_cmd(args)
    return find_state_for_string(resultjson["state"])


@exception_wrapper("Failed to login")
def login_auto():
    """
    login()
    Attempt to login automatically.
    Returns a state indicating success category.

    :returns:  speedify.State -- The speedify state enum.
    """
    resultjson = _run_speedify_cmd(["login", "auto"])
    return find_state_for_string(resultjson["state"])


@exception_wrapper("Failed to login")
def login_oauth(token: str):
    """
    login()
    Attempt to login via an oauth token.
    Returns a state indicating success category.

    :param token: The oauth token.
    :tyope token: str
    :returns:  speedify.State -- The speedify state enum.
    """
    resultjson = _run_speedify_cmd("login", "oauth", token)
    return find_state_for_string(resultjson["state"])


@exception_wrapper("Failed to logout")
def logout():
    """
    logout()
    logout.  returns the state, desc=LOGGED_OUT is a success

    :returns:  speedify.State -- The speedify state enum.
    """
    jret = _run_speedify_cmd(["logout"])
    return find_state_for_string(jret["state"])


def esni(is_on: bool = True):
    """
    esni(is_on)
    Turn esni functionality on or off.

    :param is_on: Whether esni should be on... or not.
    :type is_on: bool
    """
    if is_on is True:
        is_on = "on"
    elif is_on is False:
        is_on = "off"
    else:
        raise ValueError("is_on neither True nor False")
    return _run_speedify_cmd(["esni", is_on])


def headercompression(is_on: bool = True):
    """
    headercompression(is_on)
    Turn header compression on or off.

    :param is_on: Whether headercompression should be on... or not.
    :type is_on: bool
    """
    if is_on is True:
        is_on = "on"
    elif is_on is False:
        is_on = "off"
    else:
        raise ValueError("is_on neither True nor False")
    return _run_speedify_cmd(["headercompression", is_on])


def gateway(uri: str):
    """
    gateway(uri)

    Set the gateway uri.

    :param uri: The gateway uri.
    :type uri: str
    """
    return _run_speedify_cmd(["gateway", uri])


def daemon(method: str):
    """
    daemon(method)
    Call `method` on the daemon. Only "exit" is supported.

    :param method: The method to call. Only "exit" is available.
    """
    return _run_speedify_cmd(["daemon", method])


#
# Getter functions
#


@exception_wrapper("Failed to show server list")
def show_servers():
    """
    show_servers()
    Returns all the servers, public and private

    :returns:  dict -- :ref:`JSON server list <show-servers>` from speedify.
    """
    return _run_speedify_cmd(["show", "servers"])


@exception_wrapper("Failed to show privacy")
def show_privacy():
    """
    show_privacy()
    Returns privacy settings

    :returns:  dict -- dict -- :ref:`JSON privacy <show-privacy>` from speedify.
    """
    return _run_speedify_cmd(["show", "privacy"])


@exception_wrapper("Failed to show settings")
def show_settings():
    """
    show_settings()
    Returns current settings

    :returns:  dict -- dict -- :ref:`JSON settings <show-settings>` from speedify.
    """
    return _run_speedify_cmd(["show", "settings"])


@exception_wrapper("Failed to show adapters")
def show_adapters():
    """
    show_adapters()
    Returns current adapters

    :returns:  dict -- dict -- :ref:`JSON list of adapters <show-adapters>` from speedify.
    """
    return _run_speedify_cmd(["show", "adapters"])


@exception_wrapper("Failed to show directory")
def show_directory():
    """
    show_directory()
    Returns current directory service

    :returns:  dict -- dict -- :ref:`JSON object for the current directory service <show-directory>` from speedify.
    """
    return _run_speedify_cmd(["show", "directory"])


@exception_wrapper("Failed to do captiveportal_check")
def captiveportal_check():
    """
    captiveportal_check()
    Returns adapters which are currently blocked by a captive portal

    :returns:  dict -- dict -- :ref:`JSON list of adapters behind captive portal` from speedify.
    """
    return _run_speedify_cmd(["captiveportal", "check"])


@exception_wrapper("Failed to do captiveportal_login")
def captiveportal_login(proxy: bool = True, adapterID: str = None):
    """
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
    """
    args = ["captiveportal", "login"]
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


@exception_wrapper("Failed to show connectmethod")
def show_connectmethod():
    """
    show_connectmethod()
    Returns the current state of the 'connectmethod' setting.

    :returns dict -- :ref:`JSON connectmethod <show-connectmethod>`.
    """
    return _run_speedify_cmd(["show", "connectmethod"])


@exception_wrapper("Failed to show streamingbypass")
def show_streamingbypass():
    """
    show_streamingbypass()
    Returns the current state of the 'streamingbypass' setting.

    :returns dict -- :ref:`JSON streamingbypass <show-streamingbypass>`.
    """
    return _run_speedify_cmd(["show", "streamingbypass"])


@exception_wrapper("Failed to show disconnect")
def show_disconnect():
    """
    show_disconnect()
    Returns the last reason for a disconnection.

    :returns dict -- :ref:`JSON disconnect <show-disconnect>`.
    """
    return _run_speedify_cmd(["show", "disconnect"])


@exception_wrapper("Failed to show streaming")
def show_streaming():
    """
    show_streaming()
    Returns the current state of the 'streaming' setting.

    :returns dict -- :ref:`JSON streaming <show-streaming>`.
    """
    return _run_speedify_cmd(["show", "streaming"])


@exception_wrapper("Failed to show speedtest")
def show_speedtest():
    """
    show_speedtest()
    Returns the current results of 'speedtest'.

    :returns dict -- :ref:`JSON speedtest <show-speedtest>`.
    """
    return _run_speedify_cmd(["show", "speedtest"])


@exception_wrapper("Failed to get current server")
def show_currentserver():
    """
    show_currentserver()
    Returns current server

    :returns:  dict -- :ref:`JSON currentserver <show-currentserver>` from speedify.
    """
    return _run_speedify_cmd(["show", "currentserver"])


@exception_wrapper("Failed to get current user")
def show_user():
    """
    show_user()
    Returns current user

    :returns:  dict -- :ref:`JSON response <show-user>` from speedify.
    """
    return _run_speedify_cmd(["show", "user"])


@exception_wrapper("Failed to show connect method")
def show_connectmethod():
    """
    show_connectmethod()
    Returns the connectmethod related settings

    :returns:  :ref:`JSON response <show-connectmethod>` from speedify.
    """
    return _run_speedify_cmd(["show", "connectmethod"])


@exception_wrapper("getting state")
def show_state():
    """
    show_state()
    Returns the current state of Speedify (CONNECTED, CONNECTING, etc.)

    :returns:  speedify.State -- The speedify state enum.
    """
    resultjson = _run_speedify_cmd(["state"])
    return find_state_for_string(resultjson["state"])


@exception_wrapper("Failed to get version")
def show_version():
    """
    show_version()
    Returns speedify version

    :returns:  dict -- :ref:`JSON version <version>` from speedify.
    """
    return _run_speedify_cmd(["version"])


@exception_wrapper("Failed to show logsettings")
def show_logsettings():
    """
    show_logsettings()
    Returns current log settings

    :returns:  dict -- :ref:`JSON logsettings <show-logsettings>` from speedify.
    """
    return _run_speedify_cmd(["show", "logsettings"])


@exception_wrapper("Failed to show dscp")
def show_dscp():
    """
    show_dscp()
    Returns current DSCP queue settings

    :returns:  dict -- :ref:`JSON dscp settings <show-dscp>` from speedify.
    """
    return _run_speedify_cmd(["show", "dscp"])


@exception_wrapper("Failed to get networksharing settings")
def networksharing_settings():
    """
    networksharing_settings()
    Returns current network sharing (Pair & Share) settings

    :returns:  dict -- :ref:`JSON networksharing settings <networksharing-settings>` from speedify.
    """
    return _run_speedify_cmd(["networksharing", "settings"])


@exception_wrapper("Failed to get stats")
def safebrowsing_stats():
    args = ["safebrowsing", "stats"]
    return _run_speedify_cmd(args)


#
# Setter functions
#


@exception_wrapper("Failed to set directory server")
def directory(domain: str = ""):
    """
    directory(domain)

    Uses the given domain as the directory server.

    :param domain: The domain of the directory server.
    :type operation: str
    """
    return _run_speedify_cmd(["directory", domain])


@exception_wrapper("Failed to set DNS")
def dns(ip_addr: str = ""):
    """
    dns(ip_addr)

    Uses the given IP address for as the DNS server.

    Example:
        dns("8.8.8.8")

    :param ip_addr: The IP address of the DNS server.
    :type operation: str
    """
    return _run_speedify_cmd(["dns", ip_addr])


@exception_wrapper("Failed to add streaming bypass")
def streaming_domains_add(domains: str):
    """
    streaming_domains_add(domains)

    Add the streaming hint for some domains.

    Example:
        streaming_domains_add("example.com google.com")

    :param domains: The domains to add the streaming hint for.
    :type domains: str
    """
    return _run_speedify_cmd(["streaming", "domains", "add", domains])


@exception_wrapper("Failed to remove streaming bypass")
def streaming_domains_rem(domains: str):
    """
    streaming_domains_rem(domains)

    Remove the streaming hint for some domains.

    Example:
        streaming_domains_rem("example.com google.com")

    :param domains: The domains to remove the streaming hint from.
    :type domains: str
    """
    return _run_speedify_cmd(["streaming", "domains", "rem", domains])


@exception_wrapper("Failed to set streaming bypass")
def streaming_domains_set(domains: str):
    """
    streaming_domains_set(domains)

    Set the streaming hint for some domains.

    Example:
        streaming_domains_set("example.com google.com")

    :param domains: The domains to set the streaming hint on.
    :type domains: str
    """
    return _run_speedify_cmd(["streaming", "domains", "set", domains])


@exception_wrapper("Failed to add streaming flag")
def streaming_ipv4_add(ipv4_addrs: str):
    """
    streaming_ipv4_add(ipv4_addrs)

    Add the streaming flag for some ipv4 address(es).

    Example:
        streaming_ipv4_add(
            "68.80.59.53 55.38.18.29"
        )

    :param ipv4: The ipv4 adress(es) to add the streaming flag to.
        Example:
            "68.80.59.53 55.38.18.29"
            "68.80.59.53"
    :type ipv4_addrs: str
    """
    return _run_speedify_cmd(["streaming", "ipv4", "add", ipv4_addrs])


@exception_wrapper("Failed to remove streaming flag")
def streaming_ipv4_rem(ipv4_addrs: str):
    """
    streaming_ipv4_rem(ipv4_addrs)

    Remove the streaming flag from some ipv4 adress(es).

    Example:
        streaming_ipv4_rem(
            "68.80.59.53 55.38.18.29"
        )

    :param ipv4: The ipv4 adress(es) to remove the streaming flag from.
        Example:
            "68.80.59.53 55.38.18.29"
            "68.80.59.53"
    :type ipv4_addrs: str
    """
    return _run_speedify_cmd(["streaming", "ipv4", "rem", ipv4_addrs])


@exception_wrapper("Failed to set streaming flag")
def streaming_ipv4_set(ipv4_addrs: str):
    """
    streaming_ipv4_set(ipv4_addrs)

    Set the streaming flag on some ipv4 adress(es).

    Example:
        streaming_ipv4_set(
            "68.80.59.53 55.38.18.29"
        )

    :param ipv4: The ipv4 adress(es) to set the streaming flag on.
        Example:
            "68.80.59.53 55.38.18.29"
            "68.80.59.53"
    :type ipv4_addrs: str
    """
    return _run_speedify_cmd(["streaming", "ipv4", "set", ipv4_addrs])


@exception_wrapper("Failed to add streaming flag")
def streaming_ipv6_add(ipv6_addrs: str):
    """
    streaming_ipv6_add(ipv6_addrs)

    Add the streaming flag for some ipv6 address(es).

    Example:
        streaming_ipv6_add(
            "2001:db8:1234:ffff:ffff:ffff:ffff:0f0f 2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
        )

    :param ipv6: The ipv6 adress(es) to add the streaming flag to.
        Example:
            "2001:db8:1234:ffff:ffff:ffff:ffff:0f0f 2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
            "2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
    :type ipv6_addrs: str
    """
    return _run_speedify_cmd(["streaming", "ipv6", "add", ipv6_addrs])


@exception_wrapper("Failed to remove streaming flag")
def streaming_ipv6_rem(ipv6_addrs: str):
    """
    streaming_ipv6_rem(ipv6_addrs)

    Remove the streaming flag from some ipv6 adress(es).

    Example:
        streaming_ipv6_rem(
            "2001:db8:1234:ffff:ffff:ffff:ffff:0f0f 2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
        )

    :param ipv6: The ipv6 adress(es) to remove the streaming flag from.
        Example:
            "2001:db8:1234:ffff:ffff:ffff:ffff:0f0f 2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
            "2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
    :type ipv6_addrs: str
    """
    return _run_speedify_cmd(["streaming", "ipv6", "rem", ipv6_addrs])


@exception_wrapper("Failed to set streaming flag")
def streaming_ipv6_set(ipv6_addrs: str):
    """
    streaming_ipv6_set(ipv6_addrs)

    Set the streaming flag on some ipv6 adress(es).

    Example:
        streaming_ipv6_set(
            "2001:db8:1234:ffff:ffff:ffff:ffff:0f0f 2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
        )

    :param ipv6: The ipv6 adress(es) to set the streaming flag on.
        Example:
            "2001:db8:1234:ffff:ffff:ffff:ffff:0f0f 2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
            "2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
    :type ipv6_addrs: str
    """
    return _run_speedify_cmd(["streaming", "ipv6", "set", ipv6_addrs])


@exception_wrapper("Failed to add streaming flag")
def streaming_ports_add(ports: str):
    """
    streaming_ports_add(ports)

    Add the streaming flag for some port(s).

    Example:
        streaming_ports_add(
            "9999/tcp"
        )

    :param ports: The port(s) to add the streaming flag to.
        Example:
            "9999/tcp"
            "1500-2000/udp"
        Form:
            "<port>/<proto>"
            "<port begin>-<port end>/<proto>"
    :type ports: str
    """
    return _run_speedify_cmd(["streaming", "ports", "add", ports])


@exception_wrapper("Failed to remove streaming flag")
def streaming_ports_rem(ports: str):
    """
    streaming_ports_rem(ports)

    Remove the streaming flag from some port(s).

    Example:
        streaming_ports_rem(
            "9999/tcp"
        )

    :param ports: The port(s) to remove the streaming flag from.
        Example:
            "9999/tcp"
            "1500-2000/udp"
        Form:
            "<port>/<proto>"
            "<port begin>-<port end>/<proto>"
    :type ports: str
    """
    return _run_speedify_cmd(["streaming", "ports", "rem", ports])


@exception_wrapper("Failed to set streaming flag")
def streaming_ports_set(ports: str):
    """
    streaming_ports_set(ports)

    Set the streaming flag on some port(s).

    Example:
        streaming_ports_set(
            "9999/tcp"
        )

    :param ports: The port(s) to set the streaming flag on.
        Example:
            "9999/tcp"
            "1500-2000/udp"
        Form:
            "<port>/<proto>"
            "<port begin>-<port end>/<proto>"
    :type ports: str
    """
    return _run_speedify_cmd(["streaming", "ports", "set", ports])


@exception_wrapper("Failed to add streaming bypass")
def streamingbypass_domains_add(domains: str):
    """
    streamingbypass_domains_add(domains)

    Add a streaming bypass for some domain(s).

    Example:
        streamingbypass_domains_add(
            "example.com google.com"
        )

    :param domains: The domain(s) to add a streaming bypass to.
        Example:
            "example.com google.com"
            "google.com"
    :type domains: str
    """
    return _run_speedify_cmd(["streamingbypass", "domains", "add", domains])


@exception_wrapper("Failed to remove streaming bypass")
def streamingbypass_domains_rem(domains: str):
    """
    streamingbypass_domains_rem(domains)

    Remove a streaming bypass from some domain(s).

    Example:
        streamingbypass_domains_rem(
            "example.com google.com"
        )

    :param domains: The domain(s) to remove the streaming bypass from.
        Example:
            "example.com google.com"
            "google.com"
    :type domains: str
    """
    return _run_speedify_cmd(["streamingbypass", "domains", "rem", domains])


@exception_wrapper("Failed to set streaming bypass")
def streamingbypass_domains_set(domains: str):
    """
    streamingbypass_domains_set(domains)

    Set a streaming bypass on some domain(s).

    Example:
        streamingbypass_domains_set(
            "example.com google.com"
        )

    :param domains: The domain(s) to set the streaming bypass on.
        Example:
            "example.com google.com"
            "google.com"
    :type domains: str
    """
    return _run_speedify_cmd(["streamingbypass", "domains", "set", domains])


@exception_wrapper("Failed to add streaming bypass")
def streamingbypass_ipv4_add(ipv4_addrs: str):
    """
    streamingbypass_ipv4_add(ipv4_addrs)

    Add a streaming bypass for some ipv4 address(es).

    Example:
        streamingbypass_ipv4_add(
            "68.80.59.53 55.38.18.29"
        )

    :param ipv4_addrs: The ipv4 address(es) to add a streaming bypass to.
        Example:
            "68.80.59.53 55.38.18.29"
            "55.38.18.29"
    :type ipv4_addrs: str
    """
    return _run_speedify_cmd(["streamingbypass", "ipv4", "add", ipv4_addrs])


@exception_wrapper("Failed to remove streaming bypass")
def streamingbypass_ipv4_rem(ipv4_addrs: str):
    """
    streamingbypass_ipv4_rem(ipv4_addrs)

    Remove a streaming bypass from some ipv4 address(es).

    Example:
        streamingbypass_ipv4_rem(
            "68.80.59.53 55.38.18.29"
        )

    :param ipv4_addrs: The ipv4 address(es) to remove the streaming bypass from.
        Example:
            "68.80.59.53 55.38.18.29"
            "55.38.18.29"
    :type ipv4_addrs: str
    """
    return _run_speedify_cmd(["streamingbypass", "ipv4", "rem", ipv4_addrs])


@exception_wrapper("Failed to set streaming bypass")
def streamingbypass_ipv4_set(ipv4_addrs: str):
    """
    streamingbypass_ipv4_set(ipv4_addrs)

    Set a streaming bypass on some ipv4 address(es).

    Example:
        streamingbypass_ipv4_set(
            "68.80.59.53 55.38.18.29"
        )

    :param ipv4_addrs: The ipv4 address(es) to set the streaming bypass on.
        Example:
            "68.80.59.53 55.38.18.29"
            "55.38.18.29"
    :type ipv4_addrs: str
    """
    return _run_speedify_cmd(["streamingbypass", "ipv4", "set", ipv4_addrs])


@exception_wrapper("Failed to add streaming bypass")
def streamingbypass_ipv6_add(ipv6_addrs: str):
    """
    streamingbypass_ipv6_add(ipv6_addrs)

    Add a streaming bypass for some ipv6 address(es).

    Example:
        streamingbypass_ipv6_add(
            "2001:db8:1234:ffff:ffff:ffff:ffff:0f0f 2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
        )

    :param ipv6_addrs: The ipv6 address(es) to add a streaming bypass to.
        Example:
            "2001:db8:1234:ffff:ffff:ffff:ffff:0f0f 2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
            "2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
    :type ipv6_addrs: str
    """
    return _run_speedify_cmd(["streamingbypass", "ipv6", "add", ipv6_addrs])


@exception_wrapper("Failed to remove streaming bypass")
def streamingbypass_ipv6_rem(ipv6_addrs: str):
    """
    streamingbypass_ipv6_rem(ipv6_addrs)

    Remove a streaming bypass from some ipv6 address(es).

    Example:
        streamingbypass_ipv6_rem(
            "2001:db8:1234:ffff:ffff:ffff:ffff:0f0f 2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
        )

    :param ipv6_addrs: The ipv6 address(es) to remove the streaming bypass from.
        Example:
            "2001:db8:1234:ffff:ffff:ffff:ffff:0f0f 2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
            "2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
    :type ipv6_addrs: str
    """
    return _run_speedify_cmd(["streamingbypass", "ipv6", "rem", ipv6_addrs])


@exception_wrapper("Failed to set streaming bypass")
def streamingbypass_ipv6_set(ipv6_addrs: str):
    """
    streamingbypass_ipv6_set(ipv6_addrs)

    Set a streaming bypass on some ipv6 address(es).

    Example:
        streamingbypass_ipv6_set(
            "2001:db8:1234:ffff:ffff:ffff:ffff:0f0f 2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
        )

    :param ipv6_addrs: The ipv6 address(es) to set the streaming bypass on.
        Example:
            "2001:db8:1234:ffff:ffff:ffff:ffff:0f0f 2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
            "2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
    :type ipv6_addrs: str
    """
    return _run_speedify_cmd(["streamingbypass", "ipv6", "set", ipv6_addrs])


@exception_wrapper("Failed to add streaming bypass")
def streamingbypass_ports_add(ports: str):
    """
    streamingbypass_ports_add(ports)

    Add a streaming bypass for some port(s).

    Example:
        streamingbypass_ports_add("9999/tcp")

    :param ports: The ports to add a streaming bypass to.
        Must be of one of these forms:
            "<port>/<proto>"
            "<port begin>-<port end>/<proto>"
    :type ports: str
    """
    return _run_speedify_cmd(["streamingbypass", "ports", "add", ports])


@exception_wrapper("Failed to rem streaming bypass")
def streamingbypass_ports_rem(ports: str):
    """
    streamingbypass_ports_rem(ports)

    Remove a streaming bypass for some port(s).

    Example:
        streamingbypass_ports_rem("9999/tcp")

    :param ports: The ports to remove a streaming bypass from.
        Must be of one of these forms:
            "<port>/<proto>"
            "<port begin>-<port end>/<proto>"
    :type ports: str
    """
    return _run_speedify_cmd(["streamingbypass", "ports", "rem", ports])


@exception_wrapper("Failed to set streaming bypass")
def streamingbypass_ports_set(ports: str):
    """
    streamingbypass_ports_set(ports)

    Set a streaming bypass for some port(s).

    Example:
        streamingbypass_ports_set("9999/tcp")

    :param ports: The ports to set a streaming bypass on.
        Must be of one of these forms:
            "<port>/<proto>"
            "<port begin>-<port end>/<proto>"
    :type ports: str
    """
    return _run_speedify_cmd(["streamingbypass", "ports", "set", ports])


@exception_wrapper("Failed to set streaming bypass")
def streamingbypass_service(service_name: str, is_on: bool):
    """
    streamingbypass_service(service_name, is_on)

    Set the streaming bypass, on or off, for some pre-defined service.

    Example:
        streamingbypass_service("Netflix", True)

    :param service_name: The service to modify.
    :type service_name: str
    :param is_on: Whether to bypass the service... or not.
    :type is_on: bool
    """
    if is_on is True:
        is_on = "on"
    elif is_on is False:
        is_on = "off"
    return _run_speedify_cmd(["streamingbypass", "service", service_name, is_on])


@exception_wrapper("Failed to set adapter encryption")
def adapter_overratelimit(adapterID: str, bps: int):
    """
    adapter_overratelimit(adapterID: str, bps)

    Sets the rate limit, in bps, on adapterID.
    (show_adapters is where you find the adapterIDs).

    :param adapterID: The interface adapterID
    :type adapterID: str
    :param bps: Speed, in bps, to limit the adapter to.
    :type bps: int
    :returns:  dict -- :ref:`JSON adapter response <adapter-encryption>` from speedify.
    """
    return _run_speedify_cmd(["adapter", "overlimitratelimit", adapterID, str(bps)])


@exception_wrapper("Failed to set adapter priority")
def adapter_priority(adapterID: str, priority=Priority.ALWAYS):
    """
    adapter_priority(adapterID: str, priority=Priority.ALWAYS)
    Sets the priority on the adapter whose adapterID is provided (show_adapters is where you find the adapterIDs)

    :param adapterID: The interface adapterID
    :type adapterID: str
    :param priority: The speedify priority
    :type priority: speedify.Priority
    :returns:  dict -- :ref:`JSON adapter response <adapter-ratelimit>` from speedify.
    """
    args = ["adapter", "priority"]
    args.append(str(adapterID))
    args.append((str(priority.value)))
    resultjson = _run_speedify_cmd(args)
    return resultjson


@exception_wrapper("Failed to set adapter encryption")
def adapter_encryption(adapterID: str, should_encrypt):
    """
    adapter_encryption(adapterID: str, should_encrypt)

    Example:
        adapter_encryption("something", True)
        adapter_encryption("something", "off")

    Sets the encryption on the adapter whose adapterID is provided
    (show_adapters is where you find the adapterIDs).

    Note that any time the main encryption() function is called,
    all the per adapter encryption settings are immediately reset.

    :param adapterID: The interface adapterID
    :type adapterID: str
    :param should_encrypt: Whether to encrypt
    :type should_encrypt: bool | str
    :returns:  dict -- :ref:`JSON adapter response <adapter-encryption>` from speedify.
    """
    if should_encrypt is True:
        should_encrypt = "on"
    elif should_encrypt is False:
        should_encrypt = "off"
    should_encrypt = str(should_encrypt)
    return _run_speedify_cmd(["adapter", "encryption", adapterID, should_encrypt])


@exception_wrapper("Failed to set adapter ratelimit")
def adapter_ratelimit(adapterID: str, download_bps: int = 0, upload_bps: int = 0):
    """
    adapter_ratelimit(adapterID: str, download_bps: int = 0, upload_bps: int = 0)
    Sets the ratelimit in bps on the adapter whose adapterID is provided
    (show_adapters is where you find the adapterIDs)

    :param adapterID: The interface adapterID
    :type adapterID: str
    :param upload_bps: The upload ratelimit in bps
    :type upload_bps: int
    :param download_bps: The download ratelimit in bps
    :type download_bps: int
    :returns:  dict -- :ref:`JSON adapter response <adapter-datalimit-daily>` from speedify.
    """
    return _run_speedify_cmd(["adapter", "ratelimit", adapterID, str(download_bps), str(upload_bps)])


@exception_wrapper("Failed to set adapter daily limit")
def adapter_datalimit_daily(adapterID: str, limit: int = 0):
    """
    adapter_datalimit_daily(adapterID, limit: int = 0)
    Sets the daily usage limit in bytes on the adapter whose adapterID is provided
    (show_adapters is where you find the adapterIDs)

    :param adapterID: The interface adapterID
    :type adapterID: str
    :param limit: The daily usage limit, in bytes
    :type limit: int
    :returns:  dict -- :ref:`JSON adapter response <adapter-datalimit-daily>` from speedify
    """
    return _run_speedify_cmd(["adapter", "datalimit", "daily", adapterID, str(limit)])


@exception_wrapper("Failed to set adapter daily boost")
def adapter_datalimit_dailyboost(adapterID: str, boost: int = 0):
    """
    adapter_datalimit_dailyboost(adapterID, boost: int = 0)

    Gives some additional daily data, in bytes,
    to the adapter whose adapterID is provided.

    Show_adapters is where you find the adapterIDs.

    :param adapterID: The interface adapterID
    :type adapterID: str
    :param boost: Some additional bytes to give to the daily limit.
    :type boost: int
    :returns:  dict -- :ref:`JSON adapter response <adapter-datalimit-daily>` from speedify
    """
    return _run_speedify_cmd(["adapter", "datalimit", "dailyboost", str(boost)])


@exception_wrapper("Failed to set adapter monthly limit")
def adapter_datalimit_monthly(adapterID: str, limit: int = 0, reset_day: int = 0):
    """
    adapter_datalimit_monthly(adapterID: str, limit: int = 0, reset_day: int = 0)
    Sets the monthly usage limit in bytes on the adapter whose adapterID is provided
    (show_adapters is where you find the adapterIDs)

    :param adapterID: The interface adapterID
    :type adapterID: str
    :param limit: The monthly usage limit, in bytes
    :type limit: int
    :param reset_day: The day of the month to reset monthly usage (0-31)
    :type reset_Day: int
    :returns:  dict -- :ref:`JSON adapter response <adapter-datalimit-monthly>` from speedify.
    """
    args = ["adapter", "datalimit", "monthly", adapterID, str(limit), str(reset_day)]
    return _run_speedify_cmd(args)


@exception_wrapper("Failed to reset adapter usage")
def adapter_resetusage(adapterID: str):
    """
    adapter_resetusage(adapterID)
    Resets all the stats on this adapter back to 0.  Starts both daily and monthly limits over, if set.

    :param adapterID: The interface adapterID
    :type adapterID: str
    :returns:  dict -- :ref:`JSON adapter response <adapter-resetusage>` from speedify.
    """
    return _run_speedify_cmd(["adapter", "resetusage", adapterID])


@exception_wrapper("Failed to set forwarded ports")
def ports(tcpports: list = [], udpports: list = []):
    """
    ports(tcpports=[], udpports=[])
    sets port forwarding. call with no arguments to unset all port forwarding

    :param tcpports: List of tcp ports to forward on
    :type tcpport: list
    :param udpports: List of udp ports to forward on
    :type udpport: list
    :returns:  dict -- :ref:`JSON settings <ports>` from speedify
    """
    args = ["ports"]
    if tcpports is not None:
        for port in tcpports:
            args.append(str(port) + "/tcp")
    if udpports is not None:
        for port in udpports:
            args.append(str(port) + "/udp")

    resultjson = _run_speedify_cmd(args)
    return resultjson


@exception_wrapper("Failed to change modes")
def mode(mode: str):
    """
    mode(mode="speed")

    Uses one of 'redundant', 'speed' or 'streaming' operation modes.

    :param mode: One of:
        "redundant"
        "speed"
        "streaming"
    :type mode: str
    :returns:  dict -- :ref:`JSON settings <mode>` from speedify
    """
    return _run_speedify_cmd(["mode", mode])


@exception_wrapper("Failed to set encryption")
def encryption(should_encrypt=True):
    """
    encryption(encrypt = True)
    Sets encryption on or off.

    :param encrypt: Encrypted on or off
    :type encrypt: bool
    :returns:  dict -- :ref:`JSON settings <encryption>` from speedify
    """
    if should_encrypt is True:
        should_encrypt = "on"
    elif should_encrypt is False:
        should_encrypt = "off"
    resultjson = _run_speedify_cmd(["encryption", should_encrypt])
    return resultjson


@exception_wrapper("Failed to set jumbo")
def jumbo(mode: bool = True):
    """
    jumbo(mode = True)
    Sets jumbo MTU mode on or off.

    :param mode: Jumbo MTU on or off
    :type mode: bool
    :returns:  dict -- :ref:`JSON settings <jumbo>` from speedify
    """
    args = ["jumbo"]
    if mode == "on":
        args.append("on")
    elif mode == "off":
        args.append("off")
    elif mode is True:
        args.append("on")
    elif mode is False:
        args.append("off")
    else:
        # probably invalid, but we'll let speedify tell us THAT
        args.append(mode)

    resultjson = _run_speedify_cmd(args)
    return resultjson


@exception_wrapper("Failed to set packetaggregation")
def packetaggregation(is_on: bool = True):
    """
    packetaggregation(is_on = True)
    Sets packetaggregation mode on or off.

    :param is_on: Whether packet aggregation is on... or off.
    :type is_on: bool
    :returns:  dict -- :ref:`JSON settings <packetaggr>` from speedify
    """
    if is_on is True:
        is_on = "on"
    elif is_on is False:
        is_on = "off"
    return _run_speedify_cmd(["packetaggr", is_on])


@exception_wrapper("Failed to set killswitch")
def killswitch(killswitch: bool = False):
    """
    killswitch(killswitch = False)
    sets killswitch on or off. (Windows only)

    :param killswitch: killswitch on or off
    :type killswitch: bool
    :returns:  dict -- :ref:`JSON privacy response <privacy-killswitch>` from speedify
    """
    args = ["privacy", "killswitch"]
    args.append("on") if killswitch else args.append("off")
    resultjson = _run_speedify_cmd(args)
    return resultjson


@exception_wrapper("Failed to set overflow")
def overflow(speed_in_mbps: float = 30.0):
    """
    overflow(speed_in_mbps = 30.0)
    sets overflow threshold.

    :param speed_in_mbps: Overflow threshold in mbps
    :type speed_in_mbps: float
    :returns:  dict -- :ref:`JSON settings <overflow>` from speedify
    """
    args = ["overflow"]
    args.append(str(speed_in_mbps))
    resultjson = _run_speedify_cmd(args)
    return resultjson


@exception_wrapper("Failed to set priority overflow")
def priorityoverflow(speed_in_mbps: float = 70.0):
    """
    priorityoverflow(speed_in_mbps = 70.0)
    sets priority overflow threshold.

    :param speed_in_mbps: Priority overflow threshold in mbps
    :type speed_in_mbps: float
    :returns:  dict -- :ref:`JSON settings <priorityoverflow>` from speedify
    """
    args = ["priorityoverflow"]
    args.append(str(speed_in_mbps))
    resultjson = _run_speedify_cmd(args)
    return resultjson


@exception_wrapper("Failed to set maxredundant")
def maxredundant(num_connections: int = 5):
    """
    maxredundant(num_connections = 5)
    sets maximum number of redundant connections.

    :param num_connections: Maximum number of connections to use in redundant mode
    :type num_connections: int
    :returns:  dict -- :ref:`JSON settings <maxredundant>` from speedify
    """
    args = ["maxredundant"]
    args.append(str(num_connections))
    resultjson = _run_speedify_cmd(args)
    return resultjson


@exception_wrapper("Failed to set packet pool size")
def packetpool(size: str = "default"):
    """
    packetpool(size = "default")
    sets packet pool size.

    :param size: Packet pool size (small, default, or large)
    :type size: str
    :returns:  dict -- :ref:`JSON settings <packetpool>` from speedify
    """
    args = ["packetpool"]
    args.append(str(size))
    resultjson = _run_speedify_cmd(args)
    return resultjson


@exception_wrapper("Failed to set connect retry")
def connectretry(seconds: int = 0):
    """
    connectretry(seconds = 0)
    sets maximum connect retry timeout.

    :param seconds: Maximum number of seconds to wait between connect attempts
    :type seconds: int
    :returns:  dict -- :ref:`JSON settings <connectretry>` from speedify
    """
    args = ["connectretry"]
    args.append(str(seconds))
    resultjson = _run_speedify_cmd(args)
    return resultjson


@exception_wrapper("Failed to set transport retry")
def transportretry(seconds: int = 0):
    """
    transportretry(seconds = 0)
    sets maximum transport retry timeout.

    :param seconds: Maximum number of seconds to wait between transport attempts
    :type seconds: int
    :returns:  dict -- :ref:`JSON settings <transportretry>` from speedify
    """
    args = ["transportretry"]
    args.append(str(seconds))
    resultjson = _run_speedify_cmd(args)
    return resultjson


@exception_wrapper("Failed to set dnsleak")
def dnsleak(leak: bool = False):
    """
    dnsleak(leak = False)
    sets dnsleak on or off. (Windows only)

    :param dnsleak: dnsleak on or off
    :type dnsleak: bool
    :returns:  dict -- :ref:`JSON privacy response <privacy-dnsleak>` from speedify
    """
    args = ["privacy", "dnsleak"]
    args.append("on") if leak else args.append("off")
    resultjson = _run_speedify_cmd(args)
    return resultjson


@exception_wrapper("Failed to set startupconnect")
def startupconnect(is_on: bool = True):
    """
    startupconnect(is_on)

    Sets whether or not to automatically connect on login.

    :param is_on: Sets connect on startup on/off
    :type is_on: bool
    :returns:  dict -- :ref:`JSON settings <startupconnect>` from speedify
    """
    if is_on is True:
        is_on = "on"
    elif is_on is False:
        is_on = "off"
    else:
        raise ValueError("is_on neither True nor False")
    return _run_speedify_cmd(["startupconnect", is_on])


@exception_wrapper("Failed to set route default")
def routedefault(is_default: bool = True):
    """
    routedefault(is_default=True)
    sets whether Speedify should take the default route to the internet.
    defaults to True, only make it False if you're planning to set up
    routing rules, like IP Tables, yourself..

    :param connect: Sets routedefault on/off
    :type connect: bool
    :returns:  dict -- :ref:`JSON settings <routedefault>` from speedify
    """
    if is_default is True:
        is_default = "on"
    elif is_default is False:
        is_default = "off"
    else:
        raise ValueError("is_on neither True nor False")
    return _run_speedify_cmd(["route", "default", is_default])


@exception_wrapper("Failed to run streamtest")
def streamtest():
    """
    streamtest()

    Runs stream test.
    Returns final results.
    Will take around 30 seconds.

    :returns:  dict -- :ref:`JSON streamtest <speedtest>` from speedify
    """
    return _run_speedify_cmd(["speedtest"], cmdtimeout=600)


@exception_wrapper("Failed to run speedtest")
def speedtest():
    """
    speedtest()

    Runs speed test.
    Returns final results.
    Will take around 30 seconds.

    :returns:  dict -- :ref:`JSON speedtest <speedtest>` from speedify
    """
    jret = _run_speedify_cmd(["speedtest"], cmdtimeout=600)
    return jret


@exception_wrapper("Failed to set transport")
def transport(transport: str = "auto"):
    """
    transport(transport='auto')
    Sets the transport mode (auto/tcp/multi-tcp/udp/https).

    :param transport: Sets the transport to one of
        "auto"
        "udp"
        "tcp"
        "multi-tcp"
        "https"
    :type transport: str
    :returns:  dict -- :ref:`JSON settings <transport>` from speedify
    """
    args = ["transport", transport]
    resultjson = _run_speedify_cmd(args)
    return resultjson


@exception_wrapper("Failed getting stats")
def stats(time: int = 1):
    """
    stats(time=1)
    calls stats returns a list of all the parsed json objects it gets back

    :param time: How long to run the stats command.
    :type time: int
    :returns:  list -- list JSON stat responses from speedify.
    """
    if time == 0:
        logger.error("stats cannot be run with 0, would never return")
        raise SpeedifyError("Stats cannot be run with 0")
    if time == 1:
        # fix for bug where passing in 1 returns nothing.
        time = 2

    class list_callback:
        def __init__(self):
            self.result_list = list()

        def __call__(self, input):
            self.result_list.append(input)

    list_callback = list_callback()
    stats_callback(time, list_callback)
    return list_callback.result_list


def stats_callback(time: int, callback):
    """
    stats_callback(time, callback)
    calls stats, and callback supplied function with each line of output. 0 is forever

    :param time: How long to run the stats command.
    :type time: int
    :param callback: Callback function
    :type callback: function
    """
    args = ["stats", str(time)]
    cmd = [get_cli()] + args

    _run_long_command(cmd, callback)


@exception_wrapper("Failed to initialize safe browsing")
def safebrowsing_initialize(settings: str):
    args = ["safebrowsing", "initialize", settings]
    return _run_speedify_cmd(args)


@exception_wrapper("Failed to configure safe browsing")
def safebrowsing_configure(settings: str):
    args = ["safebrowsing", "config", settings]
    return _run_speedify_cmd(args)


@exception_wrapper("Failed to enable safe browsing")
def safebrowsing_enable(enable: bool):
    args = ["safebrowsing", "enable"]
    args.append("on") if enable else args.append("off")
    return _run_speedify_cmd(args)


@exception_wrapper("Failed getting safebrowsing error")
def safebrowsing_error(time: int = 1):
    if time == 0:
        logger.error("safebrowsing error cannot be run with 0, would never return")
        raise SpeedifyError(
            "safebrowsing error cannot be run with 0, would never return"
        )

    class list_callback:
        def __init__(self):
            self.result_list = list()

        def __call__(self, input):
            self.result_list.append(input)

    list_callback = list_callback()
    safebrowsing_error_callback(time, list_callback)
    return list_callback.result_list


def safebrowsing_error_callback(time: int, callback):
    args = ["safebrowsing", "errors", str(time)]
    cmd = [get_cli()] + args

    _run_long_command(cmd, callback)


#
# Internal functions
#


def _run_speedify_cmd(args, cmdtimeout: int = 60):
    "passes list of args to speedify command line returns the objects pulled from the json"
    resultstr = ""
    try:
        cmd = [get_cli()] + args
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=use_shell(),
            check=True,
            timeout=cmdtimeout,
        )
        resultstr = result.stdout.decode("utf-8").strip()
        sep = os.linesep * 2
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
        logger.error("Running cmd, bad json: (" + resultstr + ")")
        raise SpeedifyError("Invalid output from CLI")
    except subprocess.CalledProcessError as cpe:
        # TODO: errors can be json now
        out = cpe.stderr.decode("utf-8").strip()
        if not out:
            out = cpe.stdout.decode("utf-8").strip()
        returncode = cpe.returncode
        errorKind = "Unknown"
        if returncode == 1:
            errorKind = "Speedify API"
        elif returncode == 2:
            errorKind = "Invalid Parameter"
        elif returncode == 3:
            errorKind = "Missing Parameter"
        elif returncode == 4:
            errorKind = "Unknown Parameter"
            # whole usage message here, no help
            raise SpeedifyError(errorKind)

        newerror = None
        if returncode == 1:
            try:
                job = json.loads(out)
                if "errorCode" in job:
                    # json error! came from the speedify daemon
                    newerror = SpeedifyAPIError(
                        job["errorCode"], job["errorType"], job["errorMessage"]
                    )
            except ValueError:
                logger.error("Could not parse Speedify API Error: " + out)
                newerror = SpeedifyError(errorKind + ": Could not parse error message")
        else:
            lastline = [i for i in out.split("\n") if i][-1]
            if lastline:
                newerror = SpeedifyError(str(lastline))
            else:
                newerror = SpeedifyError(errorKind + ": " + str("Unknown error"))

        if newerror:
            raise newerror
        else:
            # treat the plain text as an error, common for valid command, with invalud arguments
            logger.error("runSpeedifyCmd CPE : " + out)
            raise SpeedifyError(errorKind + ": " + str(": " + out))


#
# Callbacks
#


# The normal _run_speedify_cmd runs the command and waits for the final output.
# these versions keep running, calling you back as json objects are emitted. useful
# for stats and for a verbose speedtest, otherwise, stick with the non-callback versions
#


@exception_wrapper("SpeedifyError in longRunCommand")
def _run_long_command(cmdarray, callback):
    "callback is a function you provide, passed parsed json objects"
    outputbuffer = ""

    with subprocess.Popen(cmdarray, stdout=subprocess.PIPE) as proc:
        for line in proc.stdout:
            line = line.decode("utf-8").strip()
            if line:
                outputbuffer += str(line)
            else:
                if outputbuffer:
                    _do_callback(callback, outputbuffer)
                    outputbuffer = ""
                else:
                    outputbuffer = ""

    if outputbuffer:
        _do_callback(callback, outputbuffer)


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
    """Finds the path for the CLI"""
    if "SPEEDIFY_CLI" in os.environ:
        possible = os.environ["SPEEDIFY_CLI"]
        if possible:
            if os.path.isfile(possible):
                logging.debug("Using cli from SPEEDIFY_CLI of (" + possible + ")")
                return possible
            else:
                logging.warning(
                    'SPEEDIFY_CLI specified a nonexistant path to cli: "'
                    + possible
                    + '"'
                )
    possible_paths = [
        "/Applications/Speedify.app/Contents/Resources/speedify_cli",
        "c://program files (x86)//speedify//speedify_cli.exe",
        "c://program files//speedify//speedify_cli.exe",
        "/usr/share/speedify/speedify_cli",
    ]
    for pp in possible_paths:
        if os.path.isfile(pp):
            logging.debug("Using cli of (" + pp + ")")
            return pp

    logging.error("Could not find speedify_cli!")
    raise SpeedifyError("Speedify CLI not found")
