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

    def test_reset(self):
        #read settings
        currentsettings = speedifysettings.get_speedify_settings()
        # write them back
        self.assertTrue(speedifysettings.apply_speedify_settings(currentsettings))

    def test_changing_settings(self):
        # now lets change a bunch of settings
        speedify.encryption(False)
        speedify.transport("udp")
        speedify.jumbo(False)
        settings = speedify.show_settings()
        self.assertFalse(settings["encrypted"])
        self.assertFalse(settings["jumboPackets"] != False)
        self.assertEqual(settings["transportMode"], "udp")

    def test_set_json(self):
        # lets use a settings string to apply it back
        json_string ='{"encryption" : false, "jumbo" : false, "transport":"tcp","adapter_priority_wifi" : "backup"}'
        self.assertTrue( speedifysettings.apply_speedify_settings(json_string))
        settings = speedify.show_settings()
        self.assertFalse(settings["encrypted"])
        self.assertFalse(settings["jumboPackets"])
        self.assertEqual( settings["transportMode"] , "tcp")

    def test_bad_json(self):
        # bad setting
        logging.disable(logging.ERROR);
        json_string ='{"encryption_nonexistant" : true}'
        self.assertFalse(speedifysettings.apply_speedify_settings(json_string))
        # wrong data type on boolean
        json_string ='{ "jumbo" :"bob", "transport":"auto"}'
        self.assertFalse(speedifysettings.apply_speedify_settings(json_string))
        # nonexistant Priority
        json_string ='{"adapter_priority_wifi" : "frank"}'
        self.assertFalse(speedifysettings.apply_speedify_settings(json_string))
        logging.disable(logging.NOTSET)

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
        mysettings = speedifysettings.get_speedify_settings()
        self.assertIn("encryption", mysettings)
        self.assertFalse(mysettings["encryption"])
        self.assertIn("transport", mysettings)
        self.assertEqual("tcp", mysettings["transport"])
        self.assertIn("jumbo", mysettings)
        self.assertTrue(mysettings["jumbo"])


if __name__ == '__main__':
    unittest.main()
    speedifysettings.apply_speedify_settings(speedifysettings.speedify_defaults)