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
# if the first command line argument is "lock" then all the settings will be generated marked as locked

logging.basicConfig(handlers=[logging.FileHandler('test.log'),logging.StreamHandler(sys.stdout)],format='%(asctime)s\t%(levelname)s\t%(module)s\t%(message)s',  level=logging.INFO)

adaptertypes = ["Wi-Fi", "Cellular", "Ethernet", "Unknown"]

def get_team_settings_as_json_string(locked=False, exportadapters=True):
    '''
    Returns the current speedify settings as a JSON string

    :returns:  str -- JSON string of speedify settings
    '''
    return json.dumps( get_team_settings(locked,exportadapters))

def get_team_settings(locked,exportadapters):
    '''
    Returns the current speedify settings as a dict

    :returns:  dict -- dict of speedify settings
    '''
    # The tree where we build our export
    settingsExport = {}

    try:
        currentsettings = speedify.show_settings();
        if exportadapters:
            adapters = speedify.show_adapters()
            #TODO: perConnectionEncryptionSettings
            #perConnectionEncryptionSettings = {}
            #settingsExport["perConnectionEncryptionSettings"] = perConnectionEncryptionSettings;
            prioritiesExport = { "Wi-Fi": {"value":"always","locked":locked},
                "Ethernet": {"value":"always","locked":locked},
                "Unknown": {"value":"always","locked":locked},
                "Cellular": {"value":"secondary","locked":locked}}
            settingsExport["priorities"] = prioritiesExport
            ratelimitExport = { "Wi-Fi": {"value":0,"locked":locked},
                "Ethernet": {"value":0,"locked":locked},
                "Unknown": {"value":0,"locked":locked},
                "Cellular": {"value":0,"locked":locked}}
            settingsExport["rateLimit"] = ratelimitExport
            monthlyLimitExport = { "Wi-Fi": {"value":{"monthlyLimit": 0,	"monthlyResetDay": 0},"locked":locked},
                "Ethernet": {"value":{"monthlyLimit": 0,	"monthlyResetDay": 0},"locked":locked},
                "Unknown": {"value":{"monthlyLimit": 0,	"monthlyResetDay": 0},"locked":locked},
                "Cellular": {"value":{"monthlyLimit": 0,	"monthlyResetDay": 0},"locked":locked}}
            dailyLimitExport = { "Wi-Fi": {"value":0,"locked":locked},
                "Ethernet": {"value":0,"locked":locked},
                "Unknown": {"value":0,"locked":locked},
                "Cellular": {"value":0,"locked":locked}}
            overlimitRateLimitExport = { "Wi-Fi": {"value":0,"locked":locked},
                "Ethernet": {"value":0,"locked":locked},
                "Unknown": {"value":0,"locked":locked},
                "Cellular": {"value":0,"locked":locked}}
            settingsExport["overlimitRateLimit"] = overlimitRateLimitExport
            encyptdefault = currentsettings["encrypted"];
            perConnectionEncryptionSettingExport = { "Wi-Fi": {"value":encyptdefault,"locked":locked},
                "Ethernet": {"value":encyptdefault,"locked":locked},
                "Unknown": {"value":encyptdefault,"locked":locked},
                "Cellular": {"value":encyptdefault,"locked":locked}}

            perConnectionEncryptionSettings = currentsettings["perConnectionEncryptionSettings"]
            anyperconnection = False
            anylimits = False

            for adapter in adapters:
                logging.debug("Adapter is :" + str(adapter))
                adaptertype= adapter["type"]
                # everything is keyed on adapter type, if you have
                # more than one adapter with same type, one of them
                # will get overwritten by the other.
                for perConnectionEncryptionSetting in perConnectionEncryptionSettings:
                    # the per connection encryption is tucked into settings instead of adapters,
                    # but you still need to look in adapters to find the adaptertype
                    if perConnectionEncryptionSetting["adapterID"] == adapter["adapterID"]:
                        encryptExport = {}
                        encryptExport["value"] = perConnectionEncryptionSetting["encrypted"]
                        encryptExport["locked"] = locked
                        anyperconnection = True
                        perConnectionEncryptionSettingExport[adaptertype] = encryptExport

                ratelimitExport[adaptertype] = {}
                ratelimitExport[adaptertype]["value"] = adapter["rateLimit"]
                ratelimitExport[adaptertype]["locked"] = locked
                prioritiesExport[adaptertype] = {}
                prioritiesExport[adaptertype]["value"] = adapter["priority"]
                prioritiesExport[adaptertype]["locked"] = locked

                if "dataUsage" in adapter:
                    limits = adapter["dataUsage"]
                    anylimits = True
                    monthlyLimitExport[adaptertype] = {}
                    monthlyLimitExport[adaptertype]["value"] = {}
                    monthlyLimitExport[adaptertype]["value"]["monthlyLimit"] = limits["usageMonthlyLimit"]
                    monthlyLimitExport[adaptertype]["value"]["monthlyResetDay"] = limits["usageMonthlyResetDay"]
                    monthlyLimitExport[adaptertype]["locked"] = locked
                    dailyLimitExport[adaptertype] = {}
                    dailyLimitExport[adaptertype]["value"] =limits["usageDailyLimit"]
                    dailyLimitExport[adaptertype]["locked"] = locked
                    overlimitRateLimitExport[adaptertype] = {}
                    overlimitRateLimitExport[adaptertype]["value"] = limits["overlimitRatelimit"]
                    overlimitRateLimitExport[adaptertype]["locked"] = locked
            # add optional sections only if they have something
            if anyperconnection:
                settingsExport["perConnectionEncryptionSetting"] = perConnectionEncryptionSettingExport
            if anylimits:
                settingsExport["monthlyLimit"] = monthlyLimitExport
                settingsExport["dailyLimit"] = dailyLimitExport
        # done with adapters
        logging.debug("Settings are:" + str( currentsettings))
        settingsExport["encrypted"] = {}
        settingsExport["encrypted"]["value"] = currentsettings["encrypted"]
        settingsExport["encrypted"]["locked"] = locked
        settingsExport["jumboPackets"] = {}
        settingsExport["jumboPackets"]["value"] = currentsettings["jumboPackets"]
        settingsExport["jumboPackets"]["locked"] = locked
        settingsExport["transportMode"] = {}
        settingsExport["transportMode"]["value"]= currentsettings["transportMode"]
        settingsExport["transportMode"]["locked"] = locked
        settingsExport["startupConnect"] = {}
        settingsExport["startupConnect"]["value"] = currentsettings["startupConnect"]
        settingsExport["startupConnect"]["locked"] = locked
        settingsExport["bondingMode"] = {}
        settingsExport["bondingMode"]["value"] = currentsettings["bondingMode"]
        settingsExport["bondingMode"]["locked"] = locked
        settingsExport["overflowThreshold"] = {}
        settingsExport["overflowThreshold"]["value"] =currentsettings["overflowThreshold"]
        settingsExport["overflowThreshold"]["locked"] = locked
        settingsExport["packetAggregation"] = {}
        settingsExport["packetAggregation"]["value"] = currentsettings["packetAggregation"]
        settingsExport["packetAggregation"]["locked"] = locked
        settingsExport["allowChaChaEncryption"] = {}
        settingsExport["allowChaChaEncryption"]["value"] = currentsettings["allowChaChaEncryption"]
        settingsExport["allowChaChaEncryption"]["locked"] = locked

        connectmethodsettings = speedify.show_connectmethod()
        settingsExport["connectMethod"] = {}
        settingsExport["connectMethod"]["value"] = speedify.connectmethod_as_string(connectmethodsettings)
        settingsExport["connectMethod"]["locked"] = locked

        if "forwardedPorts" in currentsettings:
            forwardedPortsExport = {}
            forwardedPortsExport["locked"] = locked
            forwardedPortsExport["value"] = []
            forwardedPortSettings = currentsettings["forwardedPorts"]
            for portInfo in forwardedPortSettings:
                newPortExport = {}
                newPortExport["port"] = portInfo["port"]
                newPortExport["proto"] = portInfo["protocol"]
                forwardedPortsExport["value"].append(newPortExport)
            settingsExport["forwardedPorts"] = forwardedPortsExport

        privacysettings = speedify.show_privacy()

        if "dnsLeak" in privacysettings:
            settingsExport["dnsleak"] = {}
            settingsExport["dnsleak"]["value"] = privacysettings["dnsleak"]
            settingsExport["dnsleak"]["locked"] = locked
        if "killswitch" in privacysettings:
            settingsExport["killswitch"] = {}
            settingsExport["killswitch"]["value"] =privacysettings["killswitch"]
            settingsExport["killswitch"]["locked"] = locked
        if "dnsAddresses" in privacysettings:
            settingsExport["dnsAddresses"] = {}
            settingsExport["dnsAddresses"]["locked"] = locked
            settingsExport["dnsAddresses"]["value"] = []
            for dnsserver in privacysettings["dnsAddresses"]:
                settingsExport["dnsAddresses"]["value"].append(dnsserver)
        settingsExport["crashReports"] = {}
        settingsExport["crashReports"]["value"] = privacysettings["crashReports"]
        settingsExport["crashReports"]["locked"] = locked

    except SpeedifyError as se:
        logging.error("Speedify error on getTeamSetting:"  + str(se))

    jsonExport = {}
    jsonExport["settings"] = settingsExport
    return jsonExport

lockoutput = False
exportAdapters = True
if  len(sys.argv) > 1:
    if "lock" in sys.argv :
        lockoutput = True
currentsettings = get_team_settings_as_json_string(locked=lockoutput,exportadapters=exportAdapters )
print(currentsettings)
