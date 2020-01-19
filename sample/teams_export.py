import sys
sys.path.append('../')
import speedify
import json
import os

from speedify import Priority
from speedify import SpeedifyError
import logging

# Write out the current speedify settings to std out
# In format suitable for use with the Speedify for Teams API.
logging.basicConfig(handlers=[logging.FileHandler('test.log'),logging.StreamHandler(sys.stdout)],format='%(asctime)s\t%(levelname)s\t%(module)s\t%(message)s',  level=logging.INFO)

def get_team_settings_as_json_string(locked=False):
    '''
    Returns the current speedify settings as a JSON string

    :returns:  str -- JSON string of speedify settings
    '''
    return json.dumps( get_team_settings(locked))

def get_team_settings(locked):
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
        perConnectionEncryptionSettings = {}
        settings["perConnectionEncryptionSettings"] = perConnectionEncryptionSettings;
        priorities = {}
        settings["priorities"] = priorities
        rateLimit = {}
        settings["rateLimit"] = rateLimit
        monthlyLimit = {}
        settings["monthlyLimit"] = monthlyLimit
        dailyLimit = {}
        settings["dailyLimit"] = dailyLimit
        overlimitRateLimit = {}
        settings["overlimitRateLimit"] = overlimitRateLimit

        for adapter in adapters:
            logging.debug("Adapter is :" + str(adapter))
            adaptertype= adapter["type"]
            rateLimit[adaptertype] = {}
            rateLimit[adaptertype]["value"] = adapter["rateLimit"]
            rateLimit[adaptertype]["locked"] = locked
            priorities[adaptertype] = {}
            priorities[adaptertype]["value"] = adapter["priority"]
            priorities[adaptertype]["locked"] = locked

            if "dataUsage" in adapter:
                limits = adapter["dataUsage"]
                if limits:
                    if limits["usageMonthlyLimit"]:
                        monthlyLimit[adaptertype] = {}
                        monthlyLimit[adaptertype]["value"] = {}
                        monthlyLimit[adaptertype]["value"]["monthlyLimit"] = limits["usageMonthlyLimit"]
                        monthlyLimit[adaptertype]["value"]["monthlyResetDay"] = limits["usageMonthlyResetDay"]
                        monthlyLimit[adaptertype]["locked"] = locked
                    if limits["usageDailyLimit"]:
                        dailyLimit[adaptertype] = {}
                        dailyLimit[adaptertype]["value"] =limits["usageDailyLimit"]
                        dailyLimit[adaptertype]["locked"] = locked

        currentsettings = speedify.show_settings();
        logging.debug("Settings are:" + str( currentsettings))
        settings["encrypted"] = {}
        settings["encrypted"]["value"] = currentsettings["encrypted"];
        settings["encrypted"]["locked"] = locked
        settings["jumboPackets"] = {}
        settings["jumboPackets"]["value"] = currentsettings["jumboPackets"]
        settings["jumboPackets"]["locked"] = locked
        settings["transportMode"] = {}
        settings["transportMode"]["value"]= currentsettings["transportMode"]
        settings["transportMode"]["locked"] = locked
        settings["startupConnect"] = {}
        settings["startupConnect"]["value"] = currentsettings["startupConnect"]
        settings["startupConnect"]["locked"] = locked
        settings["bondingMode"] = {}
        settings["bondingMode"]["value"] = currentsettings["bondingMode"]
        settings["bondingMode"]["locked"] = locked
        settings["overflowThreshold"] = {}
        settings["overflowThreshold"]["value"] =currentsettings["overflowThreshold"]
        settings["overflowThreshold"]["locked"] = locked
        settings["packetAggregation"] = {}
        settings["packetAggregation"]["value"] = currentsettings["packetAggregation"]
        settings["packetAggregation"]["locked"] = locked
        # not yet in schema
        #settings["route_default"] = currentsettings["enableDefaultRoute"]
        # TODO: can no longer get connectmethod back out!
        connectmethodsettings = speedify.show_connectmethod();
        settings["connectmethod"] = {}
        settings["connectmethod"]["value"] = connectmethodsettings["connectMethod"]
        settings["connectmethod"]["locked"] = locked

        privacysettings = speedify.show_privacy()
        if("dnsleak" in privacysettings):
            settings["dnsLeak"] = {}
            settings["dnsLeak"]["value"] = privacysettings["dnsleak"]
            settings["dnsLeak"]["locked"] = locked
        if("killswitch" in privacysettings):
            settings["killswitch"] = {}
            settings["killswitch"]["value"] =privacysettings["killswitch"]
            settings["killswitch"]["locked"] = locked

        # CANNOT GET  "privacy_dnsleak" or "privacy_killswitch"
        # without setting on of them

    except SpeedifyError as se:
        logging.error("Speedify error on getTeamSetting:"  + str(se))

    return settings

locked = False
if  len(sys.argv) > 1:
    if "lock" in sys.argv[1] :
        locked = True
currentsettings = get_team_settings_as_json_string(locked)
print(currentsettings)
