import datetime
import sys
import requests

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

call_webhook = False
webhook_reporting_url = None
isp_of_interest = "Starlink"
#isp_of_interest = "Comcast Cable"


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
        self.starlink_adapter_id = ""
        self.streams = {}
        # last time we reported stats to webservice rounded to nearest minute
        self.lastminute = None

    def __call__(self, callback_input):
        """Called every time a JSON object is emitted by `speedify_cli stats`.  
           Typically there a couple messages a second."""
        print("call back - "+ callback_input[0])
        try:
            if callback_input[0] == "adapters":
                # list of hardware adapters and what we know about them
                # this one is often skipped if there have been no changes
                self.adapter_callback(callback_input)
            elif callback_input[0] == "state":
                # overall speedify state: connected, connecting, etc.
                # often skipped if nothing changed
                self.state_callback(callback_input)
            elif callback_input[0] == "streaming_stats":
                # stats on high priority live streams (RTMP, VoIP, WebRTC video conferences)
                # only come if there's a stream
                self.streaming_callback(callback_input)
            elif  callback_input[0] == "session_stats":
                # session stats - totals, both current for this session and historic
                self.session_callback(callback_input)
            elif  callback_input[0] == "connection_stats":
                self.connection_callback(callback_input)
                # connection stats - about the current connections over the adapters
                pass;
        except Exception as e:
            print("callback failed because of Exception:" + str(e))
        except:
            print("callback failed for other reason")

    def send_hotkey(self,hotkey, reason):
        wsh = comctl.Dispatch("WScript.Shell")
        print("HOTKEY Ctrl-Alt-" + hotkey + " because " + reason)
        wsh.AppActivate('OBS')
        # ^% is Ctrl-Alt: https://learn.microsoft.com/en-us/dotnet/api/system.windows.forms.sendkeys?view=windowsdesktop-7.0
        wsh.SendKeys('^%' + hotkey)

    def adapter_callback(self, callback_input):
        adapterlist = callback_input[1]
        saw_starlink = False;
        for adapter in adapterlist:
            if(adapter["isp"] == isp_of_interest or adapter["adapterID"] == self.starlink_adapter_id ):
                self.starlink_adapter_id = adapter["adapterID"]
                saw_starlink = True
                starlink_state = adapter["state"]
                if(self.last_starlink_state != None and self.last_starlink_state != starlink_state ):
                    if starlink_state == "connected":
                        self.send_hotkey('w', "starlink connected")
                    elif starlink_state == "disconnected":
                        self.send_hotkey('r', "starlink disconnected")
                    elif starlink_state == "connnecting":
                        self.send_hotkey('e', "starlink connecting")
                    else:
                        print("starlink in unknown state: " + str(starlink_state) )
                self.last_starlink_state = starlink_state;
        if (self.starlink_adapter_id != "") and (not saw_starlink) and self.last_starlink_state != "disconnected":
            self.send_hotkey('r', "starlink disconnected (disappeared)")
            self.last_starlink_state = "disconnected"
  
    def connection_callback(self, callback_input):
        try:
            connections = callback_input[1]
            connectionlist = connections["connections"]
            saw_starlink = False;
            if (self.starlink_adapter_id == ""):
                return;
            for connection in connectionlist:
                #print("connection: " + connection)
                if (connection["adapterID"] == self.starlink_adapter_id):
                    saw_starlink = True
                    self.send_if_time_changed(connection)
                    pass
        except Exception as e:
            print("exception in connection_callback: " + str(e))

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
        # the streams lets us see stream by stream what's happening
        # but we just pull the sums from the ["session"]["current"] object
         
    def session_callback(self, callback_input):
        session_stats = callback_input[1]
        current = session_stats["current"]
        streaming = current["streaming"]
        totalSaves = streaming["totalFailoverSaves"] +  streaming["totalRedundantModeSaves"] +  streaming["totalSpeedModeSaves"]
        if self.last_total_saves != 0 and totalSaves > self.last_total_saves :
            # new save!  or we have no idea how many there were before, same difference
            self.send_hotkey("n","stream saved")
        self.last_total_saves = totalSaves

    def state_callback(self, callback_input):
        
        state_obj = callback_input[1]
        if "state" in state_obj:
            new_state = state_obj["state"]
            if new_state != self.last_state:
                # clear things whenever connectify state changes
                self.reset_stats()
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

    def round_time(self):
        # when the date that comes out of this function changes, then the webhook is called again.
        # currently set to time rounded down to minute
        tm = datetime.datetime.now()
        tm = tm - datetime.timedelta(
                             seconds=tm.second,
                             microseconds=tm.microsecond)
        return tm;

    def update_time(self):
        tm = self.round_time();
        self.lastminute = tm;

    def time_elapsed(self):
        # returns true if the rounded time has changed since last stored
        tm = self.round_time();
        if tm != self.lastminute:
            return True
        return False

    def send_if_time_changed(self, data):
        try:
            if not call_webhook:
                return;
            if not self.time_elapsed():
                return;
            # do report

            print("Sending connection data: " + str(data))
            x = requests.post(webhook_reporting_url, json = data)
            print(x.text)
            # success!
            self.update_time()
        except Exception as e:
            print("exception in send_if_time_changed: " + str(e))
    

    def reset_stats(self):
        """Starting our stats over, we connected or disconnected or something"""
        self.last_ssid = ""
        self.last_starlink_state = None
        self.last_bad_latency = False
        self.last_bad_loss = False
        self.last_bad_cpu = False
        self.last_bad_memory = False
        self.last_total_saves = 0
        self.streams = {}


if(len(sys.argv) > 1):
    webhook_reporting_url = sys.argv[1];
if webhook_reporting_url != None and webhook_reporting_url.startswith("http"):
    call_webhook = True

print("call_webhook: " + str(call_webhook))
speedify_callback = speedify_callback()
speedify.stats_callback(0, speedify_callback)
