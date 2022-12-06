import sys

import win32com.client as comctl



sys.path.append("../")
import speedify
import logging

logging.basicConfig(
    handlers=[logging.FileHandler("test.log"), logging.StreamHandler(sys.stdout)],
    format="%(asctime)s\t%(levelname)s\t%(module)s\t%(message)s",
    level=logging.DEBUG,
)

"""
stats_callback sample: log whenever Wi-Fi SSID or speedify state changes
Ctrl-Alt-KEY combos:
  * w = starlink connected
  * r = starlink disconnected
  * a = bad latency
  * s = bad loss
  * d = bad cpu
  * f = bad memory
  * u = speedify connected
  * y = speedify disconnected
  * i = speedify connecting
  * o = speedify disconnecting
  * n = stream saved!
"""



class speedify_callback:
    def __init__(self):
        self.last_ssid = ""
        self.last_state = None
        self.last_starlink_state = None
        self.last_bad_latency = False
        self.last_bad_loss = False
        self.last_bad_cpu = False
        self.last_bad_memory = False
        self.last_total_saves = 0

    def __call__(self, callback_input):
        if callback_input[0] == "adapters":
            self.adapter_callback(callback_input)
        elif callback_input[0] == "state":
            self.state_callback(callback_input)
        elif callback_input[0] == "streaming_stats":
            self.streaming_callback(callback_input)
        elif  callback_input[0] == "session_stats":
            self.session_callback(callback_input)


    def send_hotkey(self,hotkey, reason):
        wsh = comctl.Dispatch("WScript.Shell")
        print("HOTKEY Ctrl-Alt-" + hotkey + " because " + reason)
        wsh.AppActivate('OBS')
        # ^% is Ctrl-Alt: https://learn.microsoft.com/en-us/dotnet/api/system.windows.forms.sendkeys?view=windowsdesktop-7.0
        wsh.SendKeys('^%' + hotkey)

    def adapter_callback(self, callback_input):
        adapterlist = callback_input[1]
        for adapter in adapterlist:
            if(adapter["isp"] == "Starlink"):
                starlink_state = adapter["state"]
                if(self.last_starlink_state != None ):
                    if starlink_state == "connected":
                        self.send_hotkey('w', "starlink connected")
                    elif starlink_state == "disconnected":
                        self.send_hotkey('r', "starlink disconnected")
                self.last_starlink_state = starlink_state;
  
    def streaming_callback(self, callback_input):
        streaming_stats = callback_input[1]
        bad_latency = streaming_stats["badLatency"]
        if bad_latency and not self.last_bad_latency:
            self.send_hotkey('a', "bad latency")
        self.last_bad_latency = bad_latency
        bad_loss = streaming_stats["badLoss"]
        if bad_loss and not self.last_bad_loss:
            self.send_hotkey('s', "bad loss")
        self.last_bad_loss = bad_loss
        bad_cpu = streaming_stats["badCpu"]
        if bad_cpu and not self.last_bad_cpu:
            self.send_hotkey('d', "bad cpu")
        self.last_bad_cpu = bad_cpu
        bad_memory = streaming_stats["badMemory"]
        if bad_memory and not self.last_bad_memory:
            self.send_hotkey('f', "bad memory")
        self.last_bad_memory = bad_memory
        
    def session_callback(self, callback_input):
        session_stats = callback_input[1]
        current = session_stats["current"]
        streaming = current["streaming"]
        totalSaves = streaming["totalFailoverSaves"] +  streaming["totalRedundantModeSaves"] +  streaming["totalSpeedModeSaves"]
        if self.last_total_saves != 0 and totalSaves > self.last_total_saves :
            # new save!  or we have no idea how many there were before, same difference
            self.send_hotkey('n' "stream saved")
        self.last_total_saves = totalSaves

    def state_callback(self, callback_input):
        
        state_obj = callback_input[1]
        if "state" in state_obj:
            new_state = state_obj["state"]
            if new_state != self.last_state:
                # clear things whenever connectify state changes
                self.last_starlink_state = None
                self.last_bad_latency = False
                self.last_bad_loss = False
                self.last_bad_cpu = False
                self.last_bad_memory = False
                if self.last_state != None:
                    if new_state == "CONNECTED":                           
                        self.send_hotkey('u', "speedify connected")
                    elif new_state == "LOGGED_IN":
                        self.send_hotkey('y', "speedify disconnected")
                    elif new_state == "CONNECTING":
                        self.send_hotkey('i', "speedify connecting")
                    elif new_state == "DISCONNECTING":
                        self.send_hotkey('o', "speedify disconnecting")
                logging.info("State changed to " + new_state)
                self.last_state = new_state


speedify_callback = speedify_callback()
speedify.stats_callback(0, speedify_callback)
