import os
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
        speedify.encryption(True)
        speedify.transport("auto")
        speedify.jumbo(True)
        speedify.packetaggregation(True)
        speedify.routedefault(True)
        speedify.connectmethod("closest")
        speedify.disconnect()

    def test_dns(self):
        # @TODO is there a way to grab the current dns ip?
        logging.debug("Testing dns...")
        ips = ["8.8.8.8", ""]
        for ip in ips:
            self.assertEqual(speedify.dns(ip)["dnsAddresses"], [ip] if ip != "" else [])

    def test_streamtest(self):
        logging.info("Running streamtest...")
        if speedify.show_state() is not State.CONNECTED:
            speedify.connect("closest")
        self.assertEqual(speedify.streamtest()[0]["isError"], False)

    def test_directory(self):
        logging.debug("Testing directory settings...")
        self.assertEqual(speedify.directory()["domain"], "")

    def test_show(self):
        logging.debug("Testing show keys...")
        valid_show_keys = [
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
        for key in valid_show_keys:
            self.assertTrue(speedify.show(key) != "" and not None)

    # Not sure how to test this one
    # def test_gateway(self):
    #     logging.debug("Testing gateway settings...")
    #     speedify.gateway(str)

    def test_esni(self):
        logging.debug("Testing esni settings...")
        for b in [False, True]:
            self.assertEqual(speedify.esni(b)["enableEsni"], b)

    def test_headercompression(self):
        logging.debug("Testing header compression settings...")
        for b in [False, True]:
            self.assertEqual(speedify.headercompression(b)["headerCompression"], b)

    # Not sure how to test this one
    # def test_daemon():
    #     logging.debug("Testing daemon commands (only exit)...")
    #     speedify.daemon("exit")

    # Will not work on linux
    # def test_login_auto(self):
    #     logging.debug("Testing auto login...")
    #     self.assertTrue(
    #         speedify.login_auto() is speedify.State.CONNECTED
    #         or speedify.State.LOGGED_IN
    #     )

    # Not sure how to test this one
    # def test_login_oauth():
    #     logging.info("")
    #     speedify.login_oauth(token)

    def test_streamingbypass_domains(self):
        logging.debug("Testing streaming bypass for domains...")
        ip = "11.11.11.11"
        mode = {
            "on_add": {"op": "add", "val": True},
            "on_rem": {"op": "rem", "val": False},
        }
        for m in mode.keys():
            self.assertEqual(
                ip in speedify.streamingbypass_domains(mode[m]["op"], ip)["domains"],
                mode[m]["val"],
            )

    def test_streamingbypass_ports(self):
        logging.debug("Testing streaming bypass for ports...")

        def result_of(d):
            try:
                return d["ports"][0]["port"]
            except IndexError:
                return False

        port_num = "9999"
        mode = {
            "on_add": {"op": "add", "val": True},
            "on_rem": {"op": "rem", "val": False},
        }
        for m in mode.keys():
            self.assertEqual(
                int(port_num)
                == result_of(
                    speedify.streamingbypass_ports(mode[m]["op"], port_num + "/tcp")
                ),
                mode[m]["val"],
            )

    def test_streamingbypass_ipv4(self):
        logging.debug("Testing streaming bypass for ipv4 addresses...")
        ip = "68.80.59.53"
        mode = {
            "on_add": {"op": "add", "val": True},
            "on_rem": {"op": "rem", "val": False},
        }
        for m in mode.keys():
            self.assertEqual(
                ip in speedify.streamingbypass_ipv4(mode[m]["op"], ip)["ipv4"],
                mode[m]["val"],
            )

    def test_streamingbypass_ipv6(self):
        logging.debug("Testing streaming bypass for ipv6 addresses...")
        ip = "2001:db8:1234:ffff:ffff:ffff:ffff:f0f"
        mode = {
            "on_add": {"op": "add", "val": True},
            "on_rem": {"op": "rem", "val": False},
        }
        for m in mode.keys():
            self.assertEqual(
                ip in speedify.streamingbypass_ipv6(mode[m]["op"], ip)["ipv6"],
                mode[m]["val"],
            )

    def test_streamingbypass_service(self):
        logging.debug("Testing streaming bypass for services...")
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
        logging.info("")

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
        serverinfo = speedify.connect_closest()
        state = speedify.show_state()
        self.assertEqual(state, State.CONNECTED)
        self.assertIn("tag", serverinfo)
        self.assertIn("country", serverinfo)

    def test_connect_country(self):
        serverinfo = speedify.connect_country("sg")
        state = speedify.show_state()
        self.assertEqual(state, State.CONNECTED)
        self.assertIn("tag", serverinfo)
        self.assertIn("country", serverinfo)
        self.assertEqual(serverinfo["country"], "sg")
        new_serverinfo = speedify.show_currentserver()
        self.assertEqual(new_serverinfo["country"], "sg")

    def test_transport(self):
        mysettings = speedify.transport("https")
        speedify.connect("closest")
        mysettings = speedify.show_settings()
        self.assertEqual(mysettings["transportMode"], "https")
        # to make sure runtime changed, could check stats and look for connectionstats : connections[] : protocol
        mysettings = speedify.transport("tcp")
        self.assertEqual(mysettings["transportMode"], "tcp")
        speedify.connect("closest")
        mysettings = speedify.show_settings()
        self.assertEqual(mysettings["transportMode"], "tcp")

    def test_bad_country(self):
        logging.debug("Testing error handling, ignore next few errors")
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
        speedify.connect_closest()
        state = speedify.show_state()
        self.assertEqual(state, State.CONNECTED)
        speedify.disconnect()
        state = speedify.show_state()
        self.assertEqual(state, speedify.State.LOGGED_IN)

    def test_connectmethod(self):
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
        version = speedify.show_version()
        self.assertIn("maj", version)
        # expect at least Speedify 8.0
        self.assertGreater(version["maj"], 7)
        self.assertIn("min", version)
        self.assertIn("bug", version)
        self.assertIn("build", version)

    def test_settings(self):
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
        speedify.connect("closest")
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
            "country", server_info["country"], server_info["city"], server_info["num"]
        )
        # @TODO uncomment this
        # self.assertEqual(server_info["tag"], new_server["tag"])
        self.assertEqual(server_info["country"], new_server["country"])
        self.assertEqual(server_info["city"], new_server["city"])
        # self.assertEqual(server_info["num"], new_server["num"])

    def test_stats(self):
        speedify.connect_closest()
        report_list = speedify.stats(2)
        self.assertTrue(report_list)  # Check for non empty list
        reports = [item[0] for item in report_list]
        self.assertIn("adapters", reports)  # Check for at least one adapters report

    def test_adapters(self):
        adapters = speedify.show_adapters()
        self.assertTrue(adapters)
        adapterIDs = [adapter["adapterID"] for adapter in adapters]
        self._set_and_test_adapter_list(adapterIDs, Priority.BACKUP, 10000000)
        self._set_and_test_adapter_list(adapterIDs, Priority.ALWAYS, 0)

    def test_encryption(self):
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
