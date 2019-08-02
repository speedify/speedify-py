import os
import sys
sys.path.append('../')
import speedify
from speedify import State, Priority, SpeedifyError, SpeedifyAPIError
import speedifysettings
import logging
import unittest

logging.basicConfig(handlers=[logging.FileHandler('test.log'),logging.StreamHandler(sys.stdout)],format='%(asctime)s\t%(levelname)s\t%(module)s\t%(message)s',  level=logging.INFO)

# Test the speedify library
# assumes you're logged in

class TestSpeedify(unittest.TestCase):
    #Note doesn't test login/logout.  but then we have to deal with credentials being stored.

    def setUp(self):
        speedify.encryption(True)
        speedify.transport("auto")
        speedify.jumbo(True)
        speedify.crashreports(True)
        speedify.packetaggregation(True)
        speedify.connectmethod("closest")
        speedify.disconnect()

    def test_connect(self):
        serverinfo = speedify.connect_closest()
        state = speedify.show_state()
        self.assertEqual(state,State.CONNECTED)
        self.assertIn("tag", serverinfo)
        self.assertIn("country", serverinfo)



    def test_connect_country(self):
        serverinfo = speedify.connect_country("de")
        state = speedify.show_state()
        self.assertEqual(state,State.CONNECTED)
        self.assertIn("tag", serverinfo)
        self.assertIn("country", serverinfo)
        self.assertEqual(serverinfo["country"], "de")
        new_serverinfo = speedify.show_currentserver()
        self.assertEqual(new_serverinfo["country"], "de")

    def test_bad_country(self):
        #logging.disable(logging.ERROR);
        logging.info("Testing error handling, ignore next few errors")
        state = speedify.show_state()
        self.assertEqual(state,State.LOGGED_IN)
        logging.debug("connecting to bad country")
        with self.assertRaises(SpeedifyAPIError):
            speedify.connect_country("pp")
        logging.debug("after connecting to bad country")
        state = speedify.show_state()
        self.assertEqual(state,State.LOGGED_IN)
        logging.info("Done testing error handling")
        #logging.disable(logging.NOTSET)

    def test_disconnect(self):
        speedify.connect_closest()
        state = speedify.show_state()
        self.assertEqual(state,State.CONNECTED)
        speedify.disconnect()
        state = speedify.show_state()
        self.assertEqual(state,speedify.State.LOGGED_IN)

    def test_connectmethod(self):
        speedify.connect_closest()
        speedify.connectmethod("private", "jp")
        #pull settings from speedify to be sure they really set
        cm_settings = speedify.show_connectmethod()

        self.assertEqual(cm_settings["connectMethod"],"private")
        # country is ignored on
        self.assertEqual(cm_settings["country"], "")
        self.assertEqual(cm_settings["num"], 0)
        self.assertEqual(cm_settings["city"], "")
        speedify.connectmethod("p2p")
        cm_settings = speedify.show_connectmethod()
        self.assertEqual(cm_settings["connectMethod"],"p2p")
        self.assertEqual(cm_settings["country"], "")
        self.assertEqual(cm_settings["num"], 0)
        self.assertEqual(cm_settings["city"], "")
        retval = speedify.connectmethod("country", country="de")
        cm_settings = speedify.show_connectmethod()
        self.assertEqual(cm_settings["connectMethod"],"country")
        self.assertEqual(cm_settings["country"], "de")

        # the settings were returned by the actual connectmethod call,
        # and should be exactly the same
        self.assertEqual(cm_settings["connectMethod"],retval["connectMethod"])
        self.assertEqual(cm_settings["country"], retval["country"])
        self.assertEqual(cm_settings["num"],retval["num"])
        self.assertEqual(cm_settings["city"], retval["city"])
        speedify.connectmethod("closest")
        cm_settings = speedify.show_connectmethod()
        self.assertEqual(cm_settings["connectMethod"],"closest")
        self.assertEqual(cm_settings["country"], "")
        self.assertEqual(cm_settings["num"], 0)
        self.assertEqual(cm_settings["city"], "")

    def test_version(self):
        version = speedify.show_version()
        self.assertIn("maj",version)
        # expect at least Speedify 8.0
        self.assertGreater(version["maj"], 7)
        self.assertIn("min",version)
        self.assertIn("bug",version)
        self.assertIn("build",version)

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

    def test_privacy(self):
        speedify.crashreports(False)
        privacy_settings = speedify.show_privacy()
        self.assertFalse(privacy_settings["crashReports"])
        speedify.crashreports(True)
        privacy_settings = speedify.show_privacy()
        self.assertTrue(privacy_settings["crashReports"])
        if os.name == 'nt':
            #the windows only calls
            speedify.killswitch(True)
            privacy_settings = speedify.show_privacy()
            self.assertTrue(privacy_settings["killswitch"])
            speedify.killswitch(False)
            privacy_settings = speedify.show_privacy()
            self.assertFalse(privacy_settings["killswitch"])
        else:
            # shouldn't be there if we're not windows
            with self.assertRaises(SpeedifyError):
                logging.disable(logging.ERROR);
                speedify.killswitch(True)
                logging.disable(logging.NOTSET)

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
        connectstring = server_info["tag"]
        new_server = speedify.connect(connectstring)
        self.assertEqual(new_server["tag"], connectstring)
        self.assertEqual(server_info["country"], new_server["country"])
        self.assertEqual(server_info["city"], new_server["city"])
        self.assertEqual(server_info["num"], new_server["num"])

    def test_stats(self):
        speedify.connect_closest()
        report_list = speedify.stats(2)
        self.assertTrue(report_list) #Check for non empty list
        reports = [item[0] for item in report_list]
        self.assertIn("adapters", reports) #Check for at least one adapters report

    def test_adapters(self):
        adapters = speedify.show_adapters()
        self.assertTrue(adapters)
        adapterIDs = [adapter['adapterID'] for adapter in adapters]
        self._set_and_test_adapter_list(adapterIDs, Priority.BACKUP, 10000000)
        self._set_and_test_adapter_list(adapterIDs, Priority.ALWAYS, 0)



    def _set_and_test_adapter_list(self, adapterIDs, priority, limit):
        for adapterID in adapterIDs:
            speedify.adapter_priority(adapterID, priority)
            speedify.adapter_ratelimit(adapterID, limit)
            speedify.adapter_datalimit_daily(adapterID, limit)
            speedify.adapter_datalimit_monthly(adapterID, limit,0)
        updated_adapters = speedify.show_adapters()
        priorities = [adapter['priority'] for adapter in updated_adapters]
        rate_limits = [adapter['rateLimit'] for adapter in updated_adapters]
        daily_limits = [adapter['dataUsage']['usageDailyLimit'] for adapter in updated_adapters]
        monthly_limits = [adapter['dataUsage']['usageMonthlyLimit'] for adapter in updated_adapters]
        for set_priority, rate_limit, daily_limit, monthly_limit in zip(priorities, rate_limits, daily_limits, monthly_limits):
            # Disconnected adapters speedify is aware of will have an unchangable priority never
            if (set_priority != Priority.NEVER.value):
                self.assertEqual(set_priority, priority.value)
            self.assertEqual(rate_limit, limit)
            self.assertEqual(daily_limit, limit)
            self.assertEqual(monthly_limit, limit)

if __name__ == '__main__':
    speedifysettings.apply_speedify_settings(speedifysettings.speedify_defaults)
    unittest.main()
    speedifysettings.apply_speedify_settings(speedifysettings.speedify_defaults)
