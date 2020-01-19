#!/usr/bin/python3
# Uses Python 3.7

import speedify
import json
import logging
import os

from speedify import Priority
from speedify import SpeedifyError

"""
.. module:: speedifysettings
   :synopsis: Contains speedify cli convenience functions
"""

# for convenience, here's a JSON that resets everything to normal
speedify_defaults = '''{"connectmethod" : "closest","encryption" : true, "jumbo" : true,
    "mode" : "speed", "privacy_killswitch":false, "privacy_dnsleak": true, "privacy_crashreports": true,
    "startupconnect": true,  "packet_aggregation": true,  "transport":"auto","overflow_threshold": 30.0,
    "adapter_priority_ethernet" : "always","adapter_priority_wifi" : "always",
    "adapter_priority_cellular" : "secondary", "adapter_datalimit_daily_all" : 0,
    "adapter_datalimit_monthly_all" : 0, "adapter_ratelimit_all" : 0, "route_default": true
    }'''

def apply_setting(setting, value):
    '''
    Sets the setting to the value given

    :param setting: The speedify setting to set.
    :type setting: str
    :param value: The value to set the setting to.
    :type value: str/int
    '''
    success = True
    try:
        adapterguids = []
        logging.debug("setting: " + str(setting) + ", value:" + str(value))
        if setting.startswith("adapter_"):
            setting_split = setting.split("_")
            adaptertype = setting_split[-1]
            adapterguids = _find_adapterids(adaptertype)
            _apply_setting_to_adapters(setting,value,adapterguids)
        elif setting == "connectmethod" :
            speedify.connectmethod(value)
        elif setting == "directory":
            speedify.directory(value)
        elif setting == "encryption":
            speedify.encryption(value)
        elif setting == "packet_aggregation":
            speedify.packetaggregation(value)
        elif setting == "jumbo":
            speedify.jumbo(value)
        # dnsleak and killswitch not available on all platforms
        elif setting == "privacy_dnsleak":
            if os.name == 'nt':
                speedify.dnsleak(value)
            else:
                logging.info("dnsleak not supported on this platform")
        elif setting == "privacy_killswitch":
            if os.name == 'nt':
                speedify.killswitch(value)
            else:
                logging.info("killswitch not supported on this platform")
        elif setting == "privacy_crashreports":
            speedify.crashreports(value)
        elif setting == "mode":
            speedify.mode(value)
        elif setting == "overflow_threshold":
            speedify.overflow(float(value))
        elif setting == "route_default":
            speedify.routedefault(value)
        elif setting == "startupconnect" :
            speedify.startupconnect(value)
        elif setting == "transport" :
            speedify.transport(value)
        else:
            logging.warning("unknown setting " + str(setting))
            success = False
    except SpeedifyError as se:
        logging.error("Speedify error on setting:" + str(setting) + " value:" + str(value) + ", exception:" + str(se))
        success = False
    return success

def apply_speedify_settings(newsettings):
    '''Takes a string or parsed json of the settings, and applies them.

    :param newsettings: The JSON of speedify settings to set. May be a string or a dict
    :type setting: dict/str
    :returns:  bool -- Returns True if all settings applied, False if ANY fail
    '''
    #  possible future optimization, use show_ to pull current settings, and only change settings that changed.
    filesuccess = True
    try:
        body = {}

        if isinstance(newsettings, str):
            body = json.loads(newsettings)
        else:
            body = newsettings
        for cmd in body:
            value = body[cmd]
            filesuccess = filesuccess and apply_setting(cmd, value)
    except Exception as e:
        logging.error("Failed to apply file:" + str(e));
        filesuccess = False
    return filesuccess

def get_speedify_settings_as_json_string():
    '''
    Returns the current speedify settings as a JSON string

    :returns:  str -- JSON string of speedify settings
    '''
    return json.dumps( get_speedify_settings())

def get_speedify_settings():
    '''
    Returns the current speedify settings as a dict

    :returns:  dict -- dict of speedify settings
    '''
    settings = {}
    # pulls out the current settings... couple flaws:
    # can't get the privacy settings without changing them first, CAN get overflow_threshold
    # but the other functions can't actually set that.
    try:
        adapters = speedify.show_adapters()
        for adapter in adapters:
            logging.debug("Adapter is :" + str(adapter))
            adaptername= adapter["name"]
            settings["adapter_ratelimit_" + adaptername] = adapter["rateLimit"]
            settings["adapter_priority_" + adaptername] = adapter["priority"]
            if "dataUsage" in adapter:
                limits = adapter["dataUsage"]
                if limits:
                    if limits["usageMonthlyLimit"]:
                        settings["adapter_datalimit_monthly_" + adaptername] = limits["usageMonthlyLimit"]
                    if limits["usageDailyLimit"]:
                        settings["adapter_datalimit_daily_" + adaptername] = limits["usageDailyLimit"]

        currentsettings = speedify.show_settings();
        logging.debug("Settings are:" + str( currentsettings))
        settings["encryption"] = currentsettings["encrypted"];
        settings["jumbo"] = currentsettings["jumboPackets"]
        settings["transport"] = currentsettings["transportMode"]
        settings["startupconnect"] = currentsettings["startupConnect"]
        settings["mode"] = currentsettings["bondingMode"]
        settings["overflow_threshold"] = currentsettings["overflowThreshold"]
        settings["packet_aggregation"] = currentsettings["packetAggregation"]
        settings["route_default"] = currentsettings["enableDefaultRoute"]
        # TODO: can no longer get connectmethod back out!
        connectmethodsettings = speedify.show_connectmethod();
        settings["connectmethod"] =connectmethodsettings["connectMethod"]

        user = speedify.show_user()
        logging.debug("User is:" +str( user))
        privacysettings = speedify.show_privacy()
        if("dnsleak" in privacysettings):
            settings["privacy_dnsleak"] = privacysettings["dnsleak"]
        if("killswitch" in privacysettings):
            settings["privacy_killswitch"] = privacysettings["killswitch"]


    except SpeedifyError as se:
        logging.error("Speedify error on getSpeedfiySetting:"  + str(se))

    return settings

def _find_adapterids(adaptertype="wifi"):
    # gives you a list of Guids which match the string you pass in.  could be a type "wifi", "ethernet",
    # a name like "Ethernet 2" or "en0", or the GUID of an adapter.
    adapterGuids = []
    isGuid = False
    isAll = False
    adaptertype = adaptertype.lower()
    if (adaptertype == "wifi" ):
        # mdm takes "wifi", cli calls it "Wi-Fi", no biggie just fix
        adaptertype = "wi-fi"
    if (adaptertype.startswith("{")):
        # it's a guid!
        isGuid = True
        guid = adaptertype.lower()
    if (adaptertype == "all"):
        # applies to every adapter!  Note that there's no guarantee on order here.
        # so if you have a "_cellular" and an "_all" it's random which setting
        # the cellular will have at the end.  Would make sense to apply them in order
        # but we're just tossing them in a dictionary.
        isAll = True


    adapters = speedify.show_adapters()
    for adapter in adapters:
        if isAll:
            adapterGuids.append(str(adapter["adapterID"]))
        elif not isGuid:
            logging.debug("adapter type: " + str(adapter["type"]))
            if(adapter["type"].lower() == adaptertype):
                logging.debug("Found by type: " + str(adapter["description"]) + " guid " + str(adapter["adapterID"]))
                adapterGuids.append(str(adapter["adapterID"]))
            elif(adapter["name"].lower() == adaptertype):
                logging.debug("Found by name" + str(adapter["description"]) + " guid " + str(adapter["adapterID"]))
                adapterGuids.append(str(adapter["adapterID"]))
        else:
            if(adapter["adapterID"].lower() == guid):
                logging.debug("Found by guid, " + str(adapter["description"]) + " guid " + str(adapter["adapterID"]))
                adapterGuids.append(str(adapter["adapterID"]))
    return adapterGuids

def _apply_setting_to_adapters(setting, value, adapterguids):
    # applies one setting to an list of adapters, specified via guids
    if setting.startswith("adapter_datalimit_daily"):
        for guid in adapterguids:
            speedify.adapter_datalimit_daily(guid,value)
    elif setting.startswith("adapter_datalimit_monthly"):
        for guid in adapterguids:
            speedify.adapter_datalimit_monthly(guid,value)
    elif setting.startswith("adapter_priority"):
        try:
            for guid in adapterguids:
                speedify.adapter_priority(guid, Priority[str(value).upper()])
        except KeyError as keyerr:
            print("no such priority: " + str(value) + keyerr)
            raise
    elif setting.startswith("adapter_ratelimit"):
        for guid in adapterguids:
            speedify.adapter_ratelimit(guid,value)
