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
speedify_defaults = (
    """{"connectmethod" : "closest","encryption" : true, "jumbo" : true,
    "mode" : "speed",
    "startupconnect": true,  "packet_aggregation": true,  "transport":"auto","overflow_threshold": 30.0,
    "adapter_priority_ethernet" : "always","adapter_priority_wifi" : "always",
    "adapter_priority_cellular" : "secondary", "adapter_datalimit_daily_all" : 0,
    "adapter_datalimit_monthly_all" : 0,
    "adapter_ratelimit": {"upload_bps": 0, "download_bps": 0},
    "route_default": true
    """
    + (
        ', "privacy_killswitch":false, "privacy_dnsleak": true,'
        if os.name == "nt"
        else ""
    )
    + """
    }"""
)


def apply_setting(setting, value):
    """
    Sets the setting to the value given

    :param setting: The speedify setting to set.
    :type setting: str
    :param value: The value to set the setting to.
    :type value: str/int
    """
    success = True
    try:
        adapterguids = []
        logging.debug("setting: " + str(setting) + ", value:" + str(value))
        if setting.startswith("adapter_"):
            setting_split = setting.split("_")
            adaptertype = setting_split[-1]
            adapterguids = _find_adapterids(adaptertype)
            _apply_setting_to_adapters(setting, value, adapterguids)
        elif setting == "connectmethod":
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
            if os.name == "nt":
                speedify.dnsleak(value)
            else:
                logging.info("dnsleak not supported on this platform")
        elif setting == "privacy_killswitch":
            if os.name == "nt":
                speedify.killswitch(value)
            else:
                logging.info("killswitch not supported on this platform")
        elif setting == "mode":
            speedify.mode(value)
        elif setting == "overflow_threshold":
            speedify.overflow(float(value))
        elif setting == "route_default":
            speedify.routedefault(value)
        elif setting == "startupconnect":
            speedify.startupconnect(value)
        elif setting == "transport":
            speedify.transport(value)
        elif setting == "priority_overflow_threshold":
            speedify.priorityoverflow(float(value))
        elif setting == "max_redundant_sends":
            speedify.maxredundant(int(value))
        elif setting == "packet_pool_size":
            speedify.packetpool(str(value))
        elif setting == "maximum_connect_retry":
            speedify.connectretry(int(value))
        elif setting == "maximum_transport_retry":
            speedify.transportretry(int(value))
        # Note: allow_chacha_encryption, header_compression, automatic_connection_priority,
        # forwarded_ports, downstream_subnets, per_connection_encryption, dns_addresses,
        # request_to_disable_doh, streaming_*, bypass, localproxy_domain_watchlist,
        # daemon_log_settings, dscp_queues, and network_sharing_* settings
        # may require additional CLI command support for setting (not just getting)
        else:
            logging.warning("unknown setting " + str(setting))
            success = False
    except SpeedifyError as se:
        logging.error(
            "Speedify error on setting:"
            + str(setting)
            + " value:"
            + str(value)
            + ", exception:"
            + str(se)
        )
        success = False
    return success


def apply_speedify_settings(newsettings):
    """Takes a string or parsed json of the settings, and applies them.

    :param newsettings: The JSON of speedify settings to set. May be a string or a dict
    :type setting: dict/str
    :returns:  bool -- Returns True if all settings applied, False if ANY fail
    """
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
        logging.error("Failed to apply file:" + str(e))
        filesuccess = False
    return filesuccess


def get_speedify_settings_as_json_string():
    """
    Returns the current speedify settings as a JSON string

    :returns:  str -- JSON string of speedify settings
    """
    return json.dumps(get_speedify_settings())


def get_speedify_settings():
    """
    Returns the current speedify settings as a dict

    :returns:  dict -- dict of speedify settings
    """
    settings = {}
    # pulls out the current settings... couple flaws:
    # can't get the privacy settings without changing them first, CAN get overflow_threshold
    # but the other functions can't actually set that.
    try:
        adapters = speedify.show_adapters()
        for adapter in adapters:
            logging.debug("Adapter is :" + str(adapter))
            adaptername = adapter["name"]
            settings["adapter_ratelimit_" + adaptername] = {
                "upload_bps": adapter["rateLimit"]["uploadBps"],
                "download_bps": adapter["rateLimit"]["downloadBps"],
            }
            settings["adapter_priority_" + adaptername] = adapter["priority"]
            if "dataUsage" in adapter:
                limits = adapter["dataUsage"]
                if limits:
                    if limits["usageMonthlyLimit"]:
                        settings["adapter_datalimit_monthly_" + adaptername] = limits[
                            "usageMonthlyLimit"
                        ]
                    if limits["usageDailyLimit"]:
                        settings["adapter_datalimit_daily_" + adaptername] = limits[
                            "usageDailyLimit"
                        ]

        currentsettings = speedify.show_settings()
        logging.debug("Settings are:" + str(currentsettings))
        settings["encryption"] = currentsettings["encrypted"]
        settings["jumbo"] = currentsettings["jumboPackets"]
        settings["transport"] = currentsettings["transportMode"]
        settings["startupconnect"] = currentsettings["startupConnect"]
        settings["mode"] = currentsettings["bondingMode"]
        settings["overflow_threshold"] = currentsettings["overflowThreshold"]
        settings["packet_aggregation"] = currentsettings["packetAggregation"]
        settings["route_default"] = currentsettings["enableDefaultRoute"]

        # Additional settings from show_settings()
        settings["allow_chacha_encryption"] = currentsettings.get("allowChaChaEncryption", True)
        settings["header_compression"] = currentsettings.get("headerCompression", True)
        settings["priority_overflow_threshold"] = currentsettings.get("priorityOverflowThreshold", 70)
        settings["max_redundant_sends"] = currentsettings.get("maxRedundant", 5)
        settings["automatic_connection_priority"] = currentsettings.get("enableAutomaticPriority", True)
        settings["packet_pool_size"] = currentsettings.get("packetPoolSize", "default")
        settings["maximum_connect_retry"] = currentsettings.get("maximumConnectRetry", 1800)
        settings["maximum_transport_retry"] = currentsettings.get("maximumTransportRetry", 300)

        # Forwarded ports
        if "forwardedPorts" in currentsettings:
            settings["forwarded_ports"] = currentsettings["forwardedPorts"]

        # Downstream subnets
        if "downstreamSubnets" in currentsettings:
            settings["downstream_subnets"] = currentsettings["downstreamSubnets"]

        # Per-connection encryption settings (by adapter type)
        if "perConnectionEncryptionSettings" in currentsettings:
            per_conn_enc = {}
            for adapter_type in ["Wi-Fi", "Cellular", "Ethernet", "Unknown"]:
                if adapter_type in currentsettings["perConnectionEncryptionSettings"]:
                    per_conn_enc[adapter_type] = currentsettings["perConnectionEncryptionSettings"][adapter_type]
            if per_conn_enc:
                settings["per_connection_encryption"] = per_conn_enc

        # TODO: can no longer get connectmethod back out!
        connectmethodsettings = speedify.show_connectmethod()
        settings["connectmethod"] = connectmethodsettings["connectMethod"]

        user = speedify.show_user()
        logging.debug("User is:" + str(user))
        privacysettings = speedify.show_privacy()
        if "dnsleak" in privacysettings:
            settings["privacy_dnsleak"] = privacysettings["dnsleak"]
        if "killswitch" in privacysettings:
            settings["privacy_killswitch"] = privacysettings["killswitch"]

        # Additional privacy settings
        if "dnsAddresses" in privacysettings:
            settings["dns_addresses"] = privacysettings["dnsAddresses"]
        if "requestToDisableDoH" in privacysettings:
            settings["request_to_disable_doh"] = privacysettings["requestToDisableDoH"]

        # Streaming settings
        streamingsettings = speedify.show_streaming()
        if streamingsettings:
            if "domains" in streamingsettings:
                settings["streaming_domains"] = streamingsettings["domains"]
            if "ipv4" in streamingsettings:
                settings["streaming_ipv4"] = streamingsettings["ipv4"]
            if "ipv6" in streamingsettings:
                settings["streaming_ipv6"] = streamingsettings["ipv6"]
            if "ports" in streamingsettings:
                settings["streaming_ports"] = streamingsettings["ports"]

        # Streamingbypass (localproxy/bypass) settings
        bypasssettings = speedify.show_streamingbypass()
        if bypasssettings:
            if "domainWatchlistEnabled" in bypasssettings:
                settings["bypass"] = bypasssettings["domainWatchlistEnabled"]
            if "services" in bypasssettings:
                settings["localproxy_domain_watchlist"] = bypasssettings["services"]

        # Log settings
        logsettings = speedify.show_logsettings()
        if logsettings and "daemon" in logsettings:
            daemon_log = logsettings["daemon"]
            # Convert log level from int to string if needed
            log_level_map = {0: "error", 1: "warning", 2: "info"}
            log_level_int = daemon_log.get("logLevel", 1)
            log_level_str = log_level_map.get(log_level_int, "info")

            settings["daemon_log_settings"] = {
                "file_size": daemon_log.get("fileSize", 3145728),
                "files_per_daemon": daemon_log.get("filesPerDaemon", 3),
                "total_files": daemon_log.get("totalFiles", 9),
                "log_level": log_level_str
            }

        # DSCP settings
        dscpsettings = speedify.show_dscp()
        if dscpsettings and "dscpQueues" in dscpsettings:
            # Map CLI field names to schema field names
            dscp_queues = []
            for queue in dscpsettings["dscpQueues"]:
                dscp_queues.append({
                    "value": queue.get("dscp", 0),
                    "priority": queue.get("priority", "auto"),
                    "replication": queue.get("replication", "auto"),
                    "retransmission_attempts": queue.get("retransmissionAttempts", 2)
                })
            settings["dscp_queues"] = dscp_queues

        # Network sharing settings
        nssettings = speedify.networksharing_settings()
        if nssettings:
            settings["network_sharing_client_enabled"] = nssettings.get("clientEnabled", False)
            settings["network_sharing_host_enabled"] = nssettings.get("hostEnabled", False)
            settings["network_sharing_pair_request_behavior"] = nssettings.get("pairRequestBehavior", "ask")

    except SpeedifyError as se:
        logging.error("Speedify error on getSpeedfiySetting:" + str(se))

    return settings


def _find_adapterids(adaptertype="wifi"):
    # gives you a list of Guids which match the string you pass in.  could be a type "wifi", "ethernet",
    # a name like "Ethernet 2" or "en0", or the GUID of an adapter.
    adapterGuids = []
    isGuid = False
    isAll = False
    adaptertype = adaptertype.lower()
    if adaptertype == "wifi":
        # mdm takes "wifi", cli calls it "Wi-Fi", no biggie just fix
        adaptertype = "wi-fi"
    if adaptertype.startswith("{"):
        # it's a guid!
        isGuid = True
        guid = adaptertype.lower()
    if adaptertype == "all":
        # applies to every adapter!  Note that there's no guarantee on order here.
        # so if you have a "_cellular" and an "_all" it's random which setting
        # the cellular will have at the end.  Would make sense to apply them in order
        # but we're just tossing them in a dictionary.
        isAll = True

    adapters = speedify.show_adapters()
    for adapter in adapters:
        guid = None
        if isAll:
            adapterGuids.append(str(adapter["adapterID"]))
        elif not isGuid:
            logging.debug("adapter type: " + str(adapter["type"]))
            if adapter["type"].lower() == adaptertype:
                logging.debug(
                    "Found by type: "
                    + str(adapter["description"])
                    + " guid "
                    + str(adapter["adapterID"])
                )
                adapterGuids.append(str(adapter["adapterID"]))
            elif adapter["name"].lower() == adaptertype:
                logging.debug(
                    "Found by name"
                    + str(adapter["description"])
                    + " guid "
                    + str(adapter["adapterID"])
                )
                adapterGuids.append(str(adapter["adapterID"]))
        else:
            if adapter["adapterID"].lower() == guid:
                logging.debug(
                    "Found by guid, "
                    + str(adapter["description"])
                    + " guid "
                    + str(adapter["adapterID"])
                )
                adapterGuids.append(str(adapter["adapterID"]))
    return adapterGuids


def _apply_setting_to_adapters(setting, value, adapterguids):
    # applies one setting to an list of adapters, specified via guids
    if setting.startswith("adapter_datalimit_daily"):
        for guid in adapterguids:
            speedify.adapter_datalimit_daily(guid, value)
    elif setting.startswith("adapter_datalimit_monthly"):
        for guid in adapterguids:
            speedify.adapter_datalimit_monthly(guid, value)
    elif setting.startswith("adapter_priority"):
        try:
            for guid in adapterguids:
                speedify.adapter_priority(guid, Priority[str(value).upper()])
        except KeyError as keyerr:
            print("no such priority: " + str(value) + str(keyerr))
            raise
    elif setting.startswith("adapter_ratelimit"):
        for guid in adapterguids:
            speedify.adapter_ratelimit(guid, value["download_bps"], value["upload_bps"])
