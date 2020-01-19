import sys
sys.path.append('../')
import speedify
import speedifysettings
import logging

import unittest

logging.basicConfig(handlers=[logging.FileHandler('test.log'),logging.StreamHandler(sys.stdout)],format='%(asctime)s\t%(levelname)s\t%(module)s\t%(message)s',  level=logging.INFO)

# Test the speedifysettings library

class TestSpeedifySettings(unittest.TestCase):

    def setUp(self):
        speedify.encryption(True)
        speedify.transport("auto")
        speedify.jumbo(True)
        speedify.packetaggregation(True)
        speedify.routedefault(True)

    def test_reset(self):
        #read settings
        currentsettings = speedifysettings.get_speedify_settings()
        # write them back
        self.assertTrue(speedifysettings.apply_speedify_settings(currentsettings))

    def test_set_defaults(self):
        speedify.encryption(False)
        speedify.transport("tcp")
        self.assertTrue(speedifysettings.apply_speedify_settings(speedifysettings.speedify_defaults))
        settings = speedify.show_settings()
        self.assertTrue(settings["encrypted"])
        self.assertTrue(settings["jumboPackets"])
        self.assertEqual( settings["transportMode"] , "auto")

    def test_read_settings(self):
        speedify.encryption(False)
        speedify.transport("tcp")
        speedify.packetaggregation(False)
        mysettings = speedifysettings.get_speedify_settings()
        self.assertIn("encryption", mysettings)
        self.assertFalse(mysettings["encryption"])
        self.assertFalse(mysettings["packet_aggregation"])
        self.assertIn("transport", mysettings)
        self.assertEqual("tcp", mysettings["transport"])
        self.assertIn("jumbo", mysettings)
        self.assertTrue(mysettings["jumbo"])


    def test_set_json(self):
        # lets use a settings string to apply it back
        json_string ='{"encryption" : false, "jumbo" : false, "packet_aggregation":false,"transport":"tcp","adapter_priority_wifi" : "backup", "route_default": false}'
        self.assertTrue( speedifysettings.apply_speedify_settings(json_string))
        settings = speedify.show_settings()
        self.assertFalse(settings["encrypted"])
        self.assertFalse(settings["jumboPackets"])
        self.assertFalse(settings["packetAggregation"])
        self.assertFalse(settings["route_default"])
        self.assertEqual( settings["transportMode"] , "tcp")

    def test_bad_json(self):
        # bad setting
        logging.disable(logging.ERROR);
        json_string ='{"encryption_nonexistant" : true}'
        self.assertFalse(speedifysettings.apply_speedify_settings(json_string))
        # wrong data type on boolean
        json_string ='{ "jumbo" :"bob", "transport":"auto"}'
        self.assertFalse(speedifysettings.apply_speedify_settings(json_string))

        # nonexistent Priority
        json_string ='{"adapter_priority_all" : "frank"}'
        self.assertFalse(speedifysettings.apply_speedify_settings(json_string))

        logging.disable(logging.NOTSET)

if __name__ == '__main__':
    unittest.main()
    speedifysettings.apply_speedify_settings(speedifysettings.speedify_defaults)
