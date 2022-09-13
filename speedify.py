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


def connect(method: str = "closest", country: str = "us", city: str = None, num: int = None):
    """
    connect(method, country="us", city=None, num=None)
    Connect via one of these methods --
        closest
        public
        private
        p2p
        last
        country (in which case country is required)

    :param method: The connect method.
    :type method: str
    :param country: 2 letter country code.
    :type country: str
    :param city: The (optional) city the server is located.
    :type city: str
    :param num: The (optional) server number.
    :type num: int
    """
    args = ["connect"]
    if method == "country":
        args.append(country)
        if city is not None:
            args.append(city)
            if num is not None:
                args.append(str(num))
    elif method:
        args.append(method)
    resultjson = _run_speedify_cmd(args)
    return resultjson


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
    return connect("country", country)


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
    Login. Returns a State. Indication succes category.

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


def privacy(category: str, is_on: bool):
    """
    privacy(category, is_on)

    Configures certain privacy setting via `category` and `is_on`.
    Currently, only one setting is supported:
        "requestToDisableDoh":
            Windows-only.
            Attempt to turn DoH (DNS-over-HTTPs) functionality on or off.

    :param category: The privacy category. Currently, only "requestToDisableDoh" is supported.
    :type category: str
    :param is_on: Whether to `request` should be on... or not.
    :type is_on: bool
    """
    if is_on is True:
        is_on = "on"
    elif is_on is False:
        is_on = "off"
    else:
        raise ValueError("is_on neither True nor False")
    return _run_speedify_cmd(["privacy", category, is_on])


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


@exception_wrapper("Failed to get server list")
def show_servers():
    """
    show_servers()
    Returns all the servers, public and private

    :returns:  dict -- :ref:`JSON server list <show-servers>` from speedify.
    """
    return _run_speedify_cmd(["show", "servers"])


@exception_wrapper("Failed to get privacy")
def show_privacy():
    """
    show_privacy()
    Returns privacy settings

    :returns:  dict -- dict -- :ref:`JSON privacy <show-privacy>` from speedify.
    """
    return _run_speedify_cmd(["show", "privacy"])


@exception_wrapper("Failed to get settings")
def show_settings():
    """
    show_settings()
    Returns current settings

    :returns:  dict -- dict -- :ref:`JSON settings <show-settings>` from speedify.
    """
    return _run_speedify_cmd(["show", "settings"])


@exception_wrapper("Failed to get adapters")
def show_adapters():
    """
    show_adapters()
    Returns current adapters

    :returns:  dict -- dict -- :ref:`JSON list of adapters <show-adapters>` from speedify.
    """
    return _run_speedify_cmd(["show", "adapters"])


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


def show(item: str):
    """
    show(item)

    Returns the result, in json, of querying for `item`.

    Example:
        show("user")
        show("servers")
        show("currentserver")

    :param item: The item to query for. One of:
        "servers"
        "settings"
        "privacy"
        "adapters"
        "currentserver"
        "user"
        "directory"
        "connectmethod"
        "streamingbypass"
        "disconnect"
        "streaming"
        "speedtest"
    :type item: str
    """
    valid_items = [
        "servers",
        "settings",
        "privacy",
        "adapters",
        "currentserver",
        "user",
        "directory",
        "connectmethod",
        "streamingbypass",
        "disconnect",
        "streaming",
        "speedtest",
    ]
    if item in valid_items:
        return _run_speedify_cmd(["show", item])
    else:
        raise ValueError("Invalid item: " + item)


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


@exception_wrapper("Failed to set streaming bypass")
def streaming_domains(operation: str, domains: str):
    """
    streaming_domains(operation, domains)

    Add, remove, or set the streaming hint for some domains.

    Example:
        streaming_domains("add", "example.com google.com")
        streaming_domains("rem", "example.com google.com")

    :param operation: The operation to perform. One of:
        "add"
        "rem"
        "set"
    :type operation: str
    :param domains: The domains to .
    :type domains: str
    """
    valid_operations = ["add", "rem", "set"]
    if operation in valid_operations:
        return _run_speedify_cmd(["streaming", "domains", operation, domains])
    else:
        raise ValueError("Invalid operation: " + operation)


@exception_wrapper("Failed to set streaming ")
def streaming_ipv4(operation: str, ipv4_addrs: str):
    """
    streaming_ipv4(operation, ipv4_addrs)

    Add, remove, or set the streaming hint for some ipv4 address.

    Example:
        streaming_ipv4("add", "68.80.59.53 55.38.18.29")

    :param operation: The operation to perform. One of:
        "add"
        "rem"
        "set"
    :type operation: str
    :param ipv4_addrs: The ipv4 addresses to . Example:
        "68.80.59.53 55.38.18.29"
        "68.80.59.53"
    :type ipv4_addrs: str
    """
    valid_operations = ["add", "rem", "set"]
    if operation in valid_operations:
        return _run_speedify_cmd(["streaming", "ipv4", operation, ipv4_addrs])
    else:
        raise ValueError("Invalid operation: " + operation)


@exception_wrapper("Failed to set streaming ")
def streaming_ipv6(operation: str, ipv6_addrs: str):
    """
    streaming_ipv6(operation, ipv6_addrs)

    Add, remove, or set the streaming hint for some ipv6 address.

    Example:
        streaming_ipv6(
            "add",
            "2001:db8:1234:ffff:ffff:ffff:ffff:0f0f 2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
        )

    :param operation: The operation to perform. One of:
        "add"
        "rem"
        "set"
    :type operation: str
    :param ipv6_addrs: The ipv6 address(es) to bypass. Example:
        "2001:db8:1234:ffff:ffff:ffff:ffff:0f0f 2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
        "2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
    :type ipv6_addrs: str
    """
    valid_operations = ["add", "rem", "set"]
    if operation in valid_operations:
        return _run_speedify_cmd(["streamingbypass", "ipv6", operation, ipv6_addrs])
    else:
        raise ValueError("Invalid operation: " + operation)


@exception_wrapper("Failed to set streaming ")
def streaming_ports(operation: str, ports: str):
    """
    streaming_ports(operation, ports)

    Add, remove, or set the streaming hint for some ports.

    Example:
        streaming_ports("rem", "9999/tcp")

    :param operation: The operation to perform. One of:
        "add"
        "rem"
        "set"
    :type operation: str
    :param ports: The ports to . Must be of one of these forms:
        "<port>/<proto>"
        "<port begin>-<port end>/<proto>"
    :type ports: str
    """
    valid_operations = ["add", "rem", "set"]
    if operation in valid_operations:
        return _run_speedify_cmd(["streaming", "ports", operation, ports])
    else:
        raise ValueError("Invalid operation: " + operation)


@exception_wrapper("Failed to set streaming bypass")
def streamingbypass_domains(operation: str, domains: str):
    """
    streamingbypass_domains(operation, domains)

    Add, remove, or set the streaming bypass for some domains.

    Example:
        streamingbypass_domains("add", "example.com google.com")
        streamingbypass_domains("rem", "example.com google.com")

    :param operation: The operation to perform. One of:
        "add"
        "rem"
        "set"
    :type operation: str
    :param domains: The domains to bypass.
    :type domains: str
    """
    valid_operations = ["add", "rem", "set"]
    if operation in valid_operations:
        return _run_speedify_cmd(["streamingbypass", "domains", operation, domains])
    else:
        raise ValueError("Invalid operation: " + operation)


@exception_wrapper("Failed to set streaming bypass")
def streamingbypass_ipv4(operation: str, ipv4_addrs: str):
    """
    streamingbypass_ipv4(operation, ipv4_addrs)

    Add, remove, or set the streaming bypass for some ipv4 address.

    Example:
        streamingbypass_ipv4("add", "68.80.59.53 55.38.18.29")

    :param operation: The operation to perform. One of:
        "add"
        "rem"
        "set"
    :type operation: str
    :param ipv4_addrs: The ipv4 addresses to bypass. Example:
        "68.80.59.53 55.38.18.29"
        "68.80.59.53"
    :type ipv4_addrs: str
    """
    valid_operations = ["add", "rem", "set"]
    if operation in valid_operations:
        return _run_speedify_cmd(["streamingbypass", "ipv4", operation, ipv4_addrs])
    else:
        raise ValueError("Invalid operation: " + operation)


@exception_wrapper("Failed to set streaming bypass")
def streamingbypass_ipv6(operation: str, ipv6_addrs: str):
    """
    streamingbypass_ipv6(operation, ipv6_addrs)

    Add, remove, or set the streaming bypass for some ipv6 address.

    Example:
        streamingbypass_ipv6(
            "add",
            "2001:db8:1234:ffff:ffff:ffff:ffff:0f0f 2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
        )

    :param operation: The operation to perform. One of:
        "add"
        "rem"
        "set"
    :type operation: str
    :param ipv6_addrs: The ipv6 address(es) to bypass. Example:
        "2001:db8:1234:ffff:ffff:ffff:ffff:0f0f 2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
        "2001:db8:1234:ffff:ffff:ffff:ffff:ffff"
    :type ipv6_addrs: str
    """
    valid_operations = ["add", "rem", "set"]
    if operation in valid_operations:
        return _run_speedify_cmd(["streamingbypass", "ipv6", operation, ipv6_addrs])
    else:
        raise ValueError("Invalid operation: " + operation)


@exception_wrapper("Failed to set streaming bypass")
def streamingbypass_ports(operation: str, ports: str):
    """
    streamingbypass_ports(operation, ports)

    Add, remove, or set the streaming bypass for some ports.

    Example:
        streamingbypass_ports("rem", "9999/tcp")

    :param operation: The operation to perform. One of:
        "add"
        "rem"
        "set"
    :type operation: str
    :param ports: The ports to bypass. Must be of one of these forms:
        "<port>/<proto>"
        "<port begin>-<port end>/<proto>"
    :type ports: str
    """
    valid_operations = ["add", "rem", "set"]
    if operation in valid_operations:
        return _run_speedify_cmd(["streamingbypass", "ports", operation, ports])
    else:
        raise ValueError("Invalid operation: " + operation)


@exception_wrapper("Failed to set streaming bypass")
def streamingbypass_service(service_name: str, is_on: bool):
    """
    streamingbypass_service(service_name, is_on)

    Set the streaming bypass, on or off, for some pre-defined service.

    Example:
        streamingbypass_service("Netflix", True)

    :param service_name: The service to modify. One of:
        "Netflix"
        "Disney+"
        "HBO"
        "Hulu"
        "Peacock"
        "Amazon Prime"
        "Youtube TV"
        "Ring"
        "VoLTE"
        "Reliance Jio"
        "Microsoft Your Phone"
        "Spectrum TV & Mobile"
        "Showtime"
        "Visual Voice Mail"
        "Android Auto"
        "Tubi"
        "Hotstar"
        "RCS Messaging"
        "Ubisoft Connect"
        "Apple Updates"
    :type service_name: str
    :param is_on: Whether to bypass the service... or not.
    :type is_on: bool
    """
    valid_service_names = [
        "Netflix",
        "Disney+",
        "HBO",
        "Hulu",
        "Peacock",
        "Amazon Prime",
        "Youtube TV",
        "Ring",
        "VoLTE",
        "Reliance Jio",
        "Microsoft Your Phone",
        "Spectrum TV & Mobile",
        "Showtime",
        "Visual Voice Mail",
        "Android Auto",
        "Tubi",
        "Hotstar",
        "RCS Messaging",
        "Ubisoft Connect",
        "Apple Updates",
    ]
    if service_name in valid_service_names:
        if is_on is True:
            is_on = "on"
        elif is_on is False:
            is_on = "off"
        return _run_speedify_cmd(["streamingbypass", "service", service_name, is_on])
    else:
        raise ValueError("Invalid service name: " + service_name)


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
    return _run_speedify_cmd(["adapter", "overratelimit", adapterID, str(bps)])


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
def adapter_ratelimit(adapterID: str, ratelimit: int = 0):
    """
    adapter_ratelimit(adapterID: str, ratelimit: int = 0)
    Sets the ratelimit in bps on the adapter whose adapterID is provided
    (show_adapters is where you find the adapterIDs)

    :param adapterID: The interface adapterID
    :type adapterID: str
    :param ratelimit: The ratelimit in bps
    :type ratelimit: int
    :returns:  dict -- :ref:`JSON adapter response <adapter-datalimit-daily>` from speedify.
    """
    return _run_speedify_cmd(["adapter", "ratelimit", adapterID, str(ratelimit)])


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
