import os
import re
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append("../")

import speedify
from speedify import State, Priority, SpeedifyError, SpeedifyAPIError
import speedifysettings
import speedifyutil
import logging
import unittest
import time

logging.basicConfig(
    handlers=[logging.FileHandler("test.log"), logging.StreamHandler(sys.stdout)],
    format="%(asctime)s\t%(levelname)s\t%(module)s\t%(message)s",
    level=logging.INFO,
)

# Test the speedify library
# assumes you're logged in


class TestSpeedify(unittest.TestCase):
    # Note doesn't test login/logout.  but then we have to deal with credentials being stored.

    def setUp(self):
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        speedify.encryption(True)
        speedify.transport("auto")
        speedify.jumbo(True)
        speedify.packetaggregation(True)
        speedify.routedefault(True)
        speedify.connectmethod("closest")
        speedify.disconnect()
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)

    def test_dns(self):
        logging.debug("\n\nTesting dns...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        ips = ["8.8.8.8", ""]
        for ip in ips:
            self.assertEqual(speedify.dns(ip)["dnsAddresses"], [ip] if ip != "" else [])

    def test_streamtest(self):
        logging.debug("\n\nTesting streamtest...", end="\n")
        if speedify.show_state() is not State.CONNECTED:
            speedify.connect("closest")
        self.assertEqual(speedify.streamtest()[0]["isError"], False)

    def test_directory(self):
        logging.debug("\n\nTesting directory settings...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        result = speedify.show_directory()["domain"]
        is_prod = result == ""
        is_dev = re.search(r"devdirectory.*", result)
        self.assertTrue(is_prod or is_dev)

    def test_show(self):
        logging.debug("\n\nTesting show keys...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        show_functions = [
            speedify.show_servers,
            speedify.show_settings,
            speedify.show_privacy,
            speedify.show_adapters,
            speedify.show_currentserver,
            speedify.show_user,
            speedify.show_directory,
            speedify.show_connectmethod,
            speedify.show_streamingbypass,
            speedify.show_disconnect,
            speedify.show_streaming,
            speedify.show_speedtest,
        ]
        for f in show_functions:
            self.assertTrue(f() != "" and not None)

    def test_esni(self):
        logging.debug("\n\nTesting esni settings...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        for b in [False, True]:
            self.assertEqual(speedify.esni(b)["enableEsni"], b)

    def test_headercompression(self):
        logging.debug("\n\nTesting header compression settings...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        for b in [False, True]:
            self.assertEqual(speedify.headercompression(b)["headerCompression"], b)

    def test_streamingbypass_domains(self):
        logging.debug("\n\nTesting streaming bypass for domains...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        ip = "11.11.11.11"
        mode = {
            "on_add": {"op": speedify.streamingbypass_domains_add, "val": True},
            "on_rem": {"op": speedify.streamingbypass_domains_rem, "val": False},
        }
        for m in mode.keys():
            self.assertEqual(
                ip in mode[m]["op"](ip)["domains"],
                mode[m]["val"],
            )

    def test_streamingbypass_ports(self):
        logging.debug("\n\nTesting streaming bypass for ports...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)

        def result_of(d):
            try:
                return d["ports"][0]["port"]
            except IndexError:
                return False

        port_num = "9999"
        mode = {
            "on_add": {"op": speedify.streamingbypass_ports_add, "val": True},
            "on_rem": {"op": speedify.streamingbypass_ports_rem, "val": False},
        }
        for m in mode.keys():
            self.assertEqual(
                int(port_num) == result_of(mode[m]["op"](port_num + "/tcp")),
                mode[m]["val"],
            )

    def test_streamingbypass_ipv4(self):
        logging.debug("\n\nTesting streaming bypass for ipv4 addresses...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        ip = "68.80.59.53"
        mode = {
            "on_add": {"op": speedify.streamingbypass_ipv4_add, "val": True},
            "on_rem": {"op": speedify.streamingbypass_ipv4_rem, "val": False},
        }
        for m in mode.keys():
            self.assertEqual(
                ip in mode[m]["op"](ip)["ipv4"],
                mode[m]["val"],
            )

    def test_streamingbypass_ipv6(self):
        logging.debug("\n\nTesting streaming bypass for ipv6 addresses...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        ip = "2001:db8:1234:ffff:ffff:ffff:ffff:f0f"
        mode = {
            "on_add": {"op": speedify.streamingbypass_ipv6_add, "val": True},
            "on_rem": {"op": speedify.streamingbypass_ipv6_rem, "val": False},
        }
        for m in mode.keys():
            self.assertEqual(
                ip in mode[m]["op"](ip)["ipv6"],
                mode[m]["val"],
            )

    def test_streamingbypass_service(self):
        logging.debug("\n\nTesting streaming bypass for services...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        # I think these are still ok to test with.
        # If the get out of date:
        # speedify_cli show streamingbypass | grep title | sed -E 's/.*: (.*)/\1,/g'
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
        for s in valid_service_names:
            for b in [False, True]:
                for i in speedify.streamingbypass_service(s, b)["services"]:
                    if i["title"] == s:
                        self.assertTrue(i["enabled"] is b)

    def test_adapter_overratelimit(self):
        logging.debug("\n\nTesting overratelimit...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)

        def getrl(d):
            return d[0]["dataUsage"]["overlimitRatelimit"]

        for l in [getrl(speedify.show_adapters()), 2000000]:
            self.assertEqual(
                getrl(
                    speedify.adapter_overratelimit(
                        speedify.show_adapters()[0]["adapterID"], l
                    )
                ),
                l,
            )

    def test_connect(self):
        logging.debug("\n\nTesting connect...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        serverinfo = speedify.connect_closest()
        state = speedify.show_state()
        self.assertEqual(state, State.CONNECTED)
        self.assertIn("tag", serverinfo)
        self.assertIn("country", serverinfo)

    def test_connect_country(self):
        logging.debug("\n\nTesting connect country...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        serverinfo = speedify.connect_country("sg")
        state = speedify.show_state()
        self.assertEqual(state, State.CONNECTED)
        self.assertIn("tag", serverinfo)
        self.assertIn("country", serverinfo)
        self.assertEqual(serverinfo["country"], "sg")
        new_serverinfo = speedify.show_currentserver()
        self.assertEqual(new_serverinfo["country"], "sg")

    def test_transport(self):
        logging.debug("\n\nTesting transport...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        mysettings = speedify.transport("https")
        speedify.connect()
        mysettings = speedify.show_settings()
        self.assertEqual(mysettings["transportMode"], "https")
        # to make sure runtime changed, could check stats and look for connectionstats : connections[] : protocol
        mysettings = speedify.transport("tcp")
        self.assertEqual(mysettings["transportMode"], "tcp")
        speedify.connect()
        mysettings = speedify.show_settings()
        self.assertEqual(mysettings["transportMode"], "tcp")

    def test_bad_country(self):
        logging.debug("\n\nTesting bad country...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        logging.debug("[Testing error handling, ignore next few errors]")
        state = speedify.show_state()
        self.assertEqual(state, State.LOGGED_IN)
        logging.debug("connecting to bad country")
        with self.assertRaises(SpeedifyAPIError):
            speedify.connect_country("pp")
        logging.debug("after connecting to bad country")
        state = speedify.show_state()
        self.assertEqual(state, State.LOGGED_IN)
        logging.debug("Done testing error handling")

    def test_disconnect(self):
        logging.debug("\n\nTesting disconnect...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        speedify.connect_closest()
        state = speedify.show_state()
        self.assertEqual(state, State.CONNECTED)
        speedify.disconnect()
        state = speedify.show_state()
        self.assertEqual(state, speedify.State.LOGGED_IN)

    def test_connectmethod(self):
        logging.debug("\n\nTesting connectmethod...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        speedify.connect_closest()
        speedify.connectmethod("private", "jp")
        # pull settings from speedify to be sure they really set
        cm_settings = speedify.show_connectmethod()
        self.assertEqual(cm_settings["connectMethod"], "private")
        # country is ignored on
        self.assertEqual(cm_settings["country"], "")
        self.assertEqual(cm_settings["num"], 0)
        self.assertEqual(cm_settings["city"], "")
        speedify.connectmethod("p2p")
        cm_settings = speedify.show_connectmethod()
        self.assertEqual(cm_settings["connectMethod"], "p2p")
        self.assertEqual(cm_settings["country"], "")
        self.assertEqual(cm_settings["num"], 0)
        self.assertEqual(cm_settings["city"], "")
        retval = speedify.connectmethod("country", country="sg")
        cm_settings = speedify.show_connectmethod()
        self.assertEqual(cm_settings["connectMethod"], "country")
        self.assertEqual(cm_settings["country"], "sg")
        # the settings were returned by the actual connectmethod call,
        # and should be exactly the same
        self.assertEqual(cm_settings["connectMethod"], retval["connectMethod"])
        self.assertEqual(cm_settings["country"], retval["country"])
        self.assertEqual(cm_settings["num"], retval["num"])
        self.assertEqual(cm_settings["city"], retval["city"])
        speedify.connectmethod("closest")
        cm_settings = speedify.show_connectmethod()
        self.assertEqual(cm_settings["connectMethod"], "closest")
        self.assertEqual(cm_settings["country"], "")
        self.assertEqual(cm_settings["num"], 0)
        self.assertEqual(cm_settings["city"], "")

    def test_version(self):
        logging.debug("\n\nTesting version...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        version = speedify.show_version()
        self.assertIn("maj", version)
        # expect at least Speedify 8.0
        self.assertGreater(version["maj"], 7)
        self.assertIn("min", version)
        self.assertIn("bug", version)
        self.assertIn("build", version)

    def test_settings(self):
        logging.debug("\n\nTesting settings...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        # test some basic settings
        speedify.packetaggregation(False)
        speedify.jumbo(False)
        my_settings = speedify.show_settings()
        self.assertFalse(my_settings["packetAggregation"])
        self.assertFalse(my_settings["jumboPackets"])
        speedify.packetaggregation(True)
        speedify.jumbo(True)
        my_settings = speedify.show_settings()
        self.assertTrue(my_settings["packetAggregation"])
        self.assertTrue(my_settings["jumboPackets"])

    def test_badarguments(self):
        logging.debug("\n\nTesting bad arguments...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        # reaching into private methods to force some errors to be sure they're handled
        try:
            goterror = False
            # invalid command
            speedify._run_speedify_cmd(["invalidcommand"])
        except speedify.SpeedifyError as sapie:
            self.assertTrue("Unknown Parameter" in sapie.message)
            goterror = True
        self.assertTrue(goterror)
        try:
            # valid command, missing required argument
            goterror = False
            speedify._run_speedify_cmd(["overflow"])
        except speedify.SpeedifyError as sapie:
            self.assertTrue("Missing parameters" in sapie.message)
            goterror = True
        self.assertTrue(goterror)
        try:
            goterror = False
            # valid command, invalid argument
            speedify._run_speedify_cmd(["overflow", "bob"])
        except speedify.SpeedifyError as sapie:
            self.assertTrue("Invalid parameters" in sapie.message)
            goterror = True
        self.assertTrue(goterror)

    def test_privacy(self):
        logging.debug("\n\nTesting privacy...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        if os.name == "nt":
            # the windows only calls
            speedify.killswitch(True)
            privacy_settings = speedify.show_privacy()
            self.assertTrue(privacy_settings["killswitch"])
            speedify.killswitch(False)
            privacy_settings = speedify.show_privacy()
            self.assertFalse(privacy_settings["killswitch"])
        else:
            # shouldn't be there if we're not windows
            with self.assertRaises(SpeedifyError):
                logging.disable(logging.ERROR)
                speedify.killswitch(True)
                logging.disable(logging.NOTSET)

    def test_routedefault(self):
        logging.debug("\n\nTesting route default...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        speedify.connect()
        if not speedifyutil.using_speedify():
            time.sleep(3)
            self.assertTrue(speedifyutil.using_speedify())
        speedify.routedefault(False)
        self.assertFalse(speedify.show_settings()["enableDefaultRoute"])
        time.sleep(1)
        if speedifyutil.using_speedify():
            # try twice in case it takes a moment to settle
            time.sleep(1)
            self.assertFalse(speedifyutil.using_speedify())
        speedify.routedefault(True)
        # for whatever reason getting the route back takes longer than giving it up
        self.assertTrue(speedify.show_settings()["enableDefaultRoute"])
        time.sleep(2)
        if not speedifyutil.using_speedify():
            # try twice in case it takes a moment to settle
            time.sleep(2)
            self.assertTrue(speedifyutil.using_speedify())

    def test_serverlist(self):
        logging.debug("\n\nTesting server list...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        # also tests connecting to one server
        server_list = speedify.show_servers()
        self.assertIn("public", server_list)
        public_list = server_list["public"]
        server_info = public_list[0]
        self.assertIn("tag", server_info)
        self.assertIn("country", server_info)
        self.assertIn("city", server_info)
        self.assertIn("num", server_info)
        self.assertFalse(server_info["isPrivate"])
        new_server = speedify.connect(
            server_info["country"]
            + " "
            + server_info["city"]
            + " "
            + str(server_info["num"])
        )
        self.assertEqual(server_info["tag"], new_server["tag"])
        self.assertEqual(server_info["country"], new_server["country"])
        self.assertEqual(server_info["city"], new_server["city"])
        self.assertEqual(server_info["num"], new_server["num"])

    def test_stats(self):
        logging.debug("\n\nTesting stats...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        speedify.connect_closest()
        report_list = speedify.stats(2)
        self.assertTrue(report_list)  # Check for non empty list
        reports = [item[0] for item in report_list]
        self.assertIn("adapters", reports)  # Check for at least one adapters report

    def test_adapters(self):
        logging.debug("\n\nTesting adapters...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        adapters = speedify.show_adapters()
        self.assertTrue(adapters)
        adapterIDs = [adapter["adapterID"] for adapter in adapters]
        self._set_and_test_adapter_list(adapterIDs, Priority.BACKUP, 10000000)
        self._set_and_test_adapter_list(adapterIDs, Priority.ALWAYS, 0)

    def test_encryption(self):
        logging.debug("\n\nTesting encryption...", end="\n")
        self.assertFalse(speedify.show_state() == State.LOGGED_OUT)
        adapters = speedify.show_adapters()
        self.assertTrue(adapters)
        # just grab first adapter for testing
        adapterID = [adapter["adapterID"] for adapter in adapters][0]
        speedify.adapter_encryption(adapterID, False)
        mysettings = speedify.show_settings()
        perConnectionEncryptionEnabled = mysettings["perConnectionEncryptionEnabled"]
        self.assertTrue(perConnectionEncryptionEnabled)
        encrypted = mysettings["encrypted"]
        perConnectionEncryptionSettings = mysettings["perConnectionEncryptionSettings"]
        firstadapter = perConnectionEncryptionSettings[0]
        self.assertEqual(firstadapter["adapterID"], adapterID)
        self.assertEqual(firstadapter["encrypted"], False)
        # main thing should still be encrypted just not our one adapter
        self.assertTrue(encrypted)
        speedify.encryption(False)
        # this should both turn off encryption and wipe the custom settings
        mysettings = speedify.show_settings()
        perConnectionEncryptionEnabled = mysettings["perConnectionEncryptionEnabled"]
        self.assertFalse(perConnectionEncryptionEnabled)
        encrypted = mysettings["encrypted"]
        self.assertFalse(encrypted)
        # now let's test with only the adapter being encrypted
        speedify.adapter_encryption(adapterID, True)
        mysettings = speedify.show_settings()
        perConnectionEncryptionEnabled = mysettings["perConnectionEncryptionEnabled"]
        self.assertTrue(perConnectionEncryptionEnabled)
        encrypted = mysettings["encrypted"]
        perConnectionEncryptionSettings = mysettings["perConnectionEncryptionSettings"]
        firstadapter = perConnectionEncryptionSettings[0]
        self.assertEqual(firstadapter["adapterID"], adapterID)
        self.assertEqual(firstadapter["encrypted"], True)
        speedify.encryption(True)
        # this should both turn on encryption and wipe the custom settings
        mysettings = speedify.show_settings()
        perConnectionEncryptionEnabled = mysettings["perConnectionEncryptionEnabled"]
        self.assertFalse(perConnectionEncryptionEnabled)
        encrypted = mysettings["encrypted"]
        self.assertTrue(encrypted)

    def _set_and_test_adapter_list(self, adapterIDs, priority, limit):
        for adapterID in adapterIDs:
            speedify.adapter_priority(adapterID, priority)
            speedify.adapter_ratelimit(adapterID, limit)
            speedify.adapter_datalimit_daily(adapterID, limit)
            speedify.adapter_datalimit_monthly(adapterID, limit, 0)
        updated_adapters = speedify.show_adapters()
        priorities = [adapter["priority"] for adapter in updated_adapters]
        rate_limits = [adapter["rateLimit"] for adapter in updated_adapters]
        daily_limits = [
            adapter["dataUsage"]["usageDailyLimit"] for adapter in updated_adapters
        ]
        monthly_limits = [
            adapter["dataUsage"]["usageMonthlyLimit"] for adapter in updated_adapters
        ]
        for set_priority, rate_limit, daily_limit, monthly_limit in zip(
            priorities, rate_limits, daily_limits, monthly_limits
        ):
            # Disconnected adapters speedify is aware of will have an unchangable priority never
            if set_priority != Priority.NEVER.value:
                self.assertEqual(set_priority, priority.value)
            self.assertEqual(rate_limit, limit)
            self.assertEqual(daily_limit, limit)
            self.assertEqual(monthly_limit, limit)


if __name__ == "__main__":
    speedifysettings.apply_speedify_settings(speedifysettings.speedify_defaults)
    unittest.main()
    speedifysettings.apply_speedify_settings(speedifysettings.speedify_defaults)
