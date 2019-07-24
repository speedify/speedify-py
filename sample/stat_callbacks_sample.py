import sys
sys.path.append('../')
import speedify
import logging

logging.basicConfig(handlers=[logging.FileHandler('test.log'),logging.StreamHandler(sys.stdout)],format='%(asctime)s\t%(levelname)s\t%(module)s\t%(message)s',  level=logging.DEBUG)

'''
stats_callback sample: log whenever Wi-Fi SSID or speedify state changes
'''

class speedify_callback():
    def __init__( self ):
        self.last_ssid = ""
        self.last_state = None
    def __call__(self, callback_input):
        if(callback_input[0] == "adapters"):
            self.adapter_callback(callback_input)
        elif (callback_input[0] == "state"):
            self.state_callback(callback_input)

    def adapter_callback(self, callback_input):
        networklist = callback_input[1]
        for network in networklist:
            if (network["type"] == "Wi-Fi") and (network["state"] == "connected"):
                if "connectedNetworkName" in network:
                    ssid =  network["connectedNetworkName"]
                    if not self.last_ssid == ssid:
                        logging.info("SSID changed to " + ssid)
                        self.last_ssid=ssid

    def state_callback(self, callback_input):
        state_obj = callback_input[1]
        if "state" in state_obj:
            new_state = state_obj["state"]
            if new_state != self.last_state:
                logging.info("State changed to " + new_state)
                self.last_state = new_state

speedify_callback = speedify_callback()
speedify.stats_callback(0, speedify_callback)
