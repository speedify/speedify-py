import time
import sys
from win10toast import ToastNotifier
# cross platform notifier... not using now
# from notifypy import Notify
sys.path.append('../')
import speedify
from speedify import State, SpeedifyError, Priority

# This program uses the speedify_cli to watch speedify for state and live streaming
# and shows hte users appropriate notifications.

# The Notification code is Windows only.  Everything else should work on macOS
# or Linux.  (but i haven't tried)


# if there's an issue we look for a possible cause in:
# * latency
# * loss
# * Cpu
# * Memory
# And then we show an inapp message and possible an native notification.

# Other things we don't look at, but might make some sense:
#  * Busy GPU - i only see code/clil for checking NVIDIA GPUs even though task manager shows it for any GPU
#  * Congestion - internet not fast enough for stream...  don't really see this in the cli output
#  * Loss of internet during stream
#  * Low Wifi signal strength
#  * internet connections disconnecting?
#  * Jitter

# Issues:
#  * Notification is making a noise every time now.  I want silent notificaitons, the person is streaming!  fix https://stackoverflow.com/questions/56695061/is-there-any-way-to-disable-the-notification-sound-on-win10toast-python-library
#  * Not using the crossplatform notification library, would work on linux and mac if i did that
#  * Notifications show the app name as 'Python'.  It's true, and this is a prototype, so whatever.
#  * Wonder if there's a way to tell if there's  congestion that's causing stream to not hit full speed?

# If you don't see the notifications, it probably means you have Windows Focus Assist on.  Turn it off.

# delay between loops.  but the speedify.stats(1) takes more than a second so
# the loop is much slower than this
delay = 1

toaster = ToastNotifier()


# show a native notification
def notify(title, msg):
    global toaster
    try:
        # using win10toast... annoytingly does not have a silent option, though
        # the stackoverflow question above explains how to patch it, i don't care enough
        # for a throw away prototype
        toaster.show_toast(str(title),str(msg),icon_path="SpeedifyApp.ico")
        print("Toast: " +str(title) + " / " + str(msg))
    except Exception as e:
        print("Error showing notification " + str(e))
        # seems like it can get stuck and never recover.  so let's try making a new one?
        toaster = ToastNotifier()

# show a banner in the app... really just prints a line
def inapp_banner(title, subtitle, level="info"):
    print("text-banner: " + title + " / " + subtitle + " (" + level +")")

 # Main function
def main():
    # just to make us not keep printing "no streams" endlessly when not is_streaming
    no_streams_notified = True

    is_streaming = False
    bad_latency = False
    bad_loss = False
    bad_cpu = False
    bad_memory = False
    current_state = "DISCONNECTED"
    current_streams = {}

    bad_internet_notified = False
    # are any streams showing possible problems?
    problems_yellow = False
    # are any streams in terrible shape?
    problems_red = False
    # do any streams seem stopped?
    problems_grey = False
    # did we notify user about running out of memory?
    bad_memory_notified = False
    # did we notifiy user about running out of cpu?
    bad_cpu_notified = False

    while True:
        try:
            problems_yellow = False
            problems_red = False
            problems_grey = False
            stats = speedify.stats(1)
            for json_array in stats:
                #print("object type: " + str(json_array[0]))
                if(str(json_array[0]) == "streaming_stats"):
                    streaming_right_now = False
                    #print("      Item: " + str(json_array))

                    json_dict = json_array[1]
                    if "badLoss" in json_dict:
                        bad_loss = json_dict["badLoss"]
                    if "badLatency" in json_dict:
                        bad_latency = json_dict["badLatency"]
                        if bad_latency:
                            print(str(stats))
                    if "badCpu" in json_dict:
                        # bools... trying to decide if this is nice
                        # and simple and nothing but actionable, or
                        # if I'd like to know the % to show as well.
                        # unsure, rolling with the bool to see if
                        # its good enough
                        bad_cpu = json_dict["badCpu"]
                    if "badMemory" in json_dict:
                        bad_memory = json_dict["badMemory"]
                    if bad_cpu or bad_loss or bad_latency or bad_memory:
                        print("    bad_cpu: " +str(bad_cpu) + " bad_memory: " + str(bad_memory) + " bad_latency: " + str(bad_latency) + " bad_loss: " + str(bad_loss))

                    #print("json_dict" + str(json_dict))
                    streams_array = json_dict["streams"]
                    new_streams = {}
                    for stream in streams_array :
                        stream_id = stream["id"]
                        new_streams[stream_id] = stream
                        warning = ""
                        old_stream = None
                        if stream_id in current_streams:
                            old_stream = current_streams[stream_id]

                        if stream["active"] == True:
                            streaming_right_now = True
                            if "name" in stream:
                                app_name = stream["name"]
                            health = "good"
                            if "health" in stream:
                                health = stream["health"]
                            print("     " + str(app_name) + " health: " +str(health))

                            # Based on what we know, classify to a color.
                            # Green - all is well, we're streaming!
                            color = "Green"
                            if health == "stopped":
                                # no data for 3 seconds?  Probably disconnected?
                                color = "Grey"
                                problems_grey = True
                            elif health == "poor":
                                # below average for 3 seconds, or no data for 2?  probably having bad time
                                color = "Yellow"
                                if bad_loss or bad_latency:
                                    # also loss or latency?  Things must be bad.
                                    color = "Red"
                                    problems_red = True
                                else:
                                    problems_yellow = True
                            stream["color"] = color
                            print("[" + color + "] Streaming " + app_name + " " + warning)

                    is_streaming = streaming_right_now
                    if not is_streaming:
                        is_streaming = False
                        bad_latency = False
                        slow_count=0
                        bad_loss = False
                        bad_cpu= False
                        bad_memory = False
                        bad_internet_notified = False
                        bad_cpu_notified = False
                        bad_memory_notified = False
                    current_streams = new_streams
                if(str(json_array[0]) == "state"):
                    state_obj = json_array[1]
                    new_state = state_obj["state"]
                    if new_state!="CONNECTED":
                        # disconnected, reset all the stats
                        is_streaming = False
                        bad_latency = False
                        bad_loss = False
                        bad_cpu= False
                        bad_memory = False
                        bad_internet_notified = False
                        bad_cpu_notified = False
                        bad_memory_notified = False
                    current_state = new_state

            # POST STATS
            if(is_streaming):
                no_streams_notified = False
                print ("")
                # Each notification can only be shown once per streaming session.
                # a streaming session is casually defined as starting when first
                # stream starts, and ends when last stream ends.  Because, for example,
                # microsoft teams often shows up as 5 streams, and i don't want 5 of the
                # same notifications during that call.

                if not bad_internet_notified and (bad_loss or bad_latency):
                    msg = ""
                    if bad_loss :
                        msg = "Loss is high, "
                    if bad_latency:
                        msg = msg+ "Latency is high, "
                    notify("Unstable Connection", msg +" can you move to get better signal?")
                    bad_internet_notified = True

                if bad_memory:
                    if not bad_memory_notified:
                        notify("Low Memory","Can you close some apps or tabs?")
                    bad_memory_notified = True

                # notification on CPU while streaming
                # should this only be done while there are problems?
                if bad_cpu and not bad_cpu_notified:
                    # i took out the count stuff, expect this to be too spastic,
                    # showing too many notifications.
                    bad_cpu_notified = True
                    notify("CPU Busy", "Can you close some apps or tabs?")

                ### BANNERS!!!
                # Inapp banners while streaming to show the user if there's an issue
                level = "info"
                if problems_yellow or problems_grey:
                    level = "warning"
                if problems_red:
                    level = "error"
                # banners at the bottom of the UI if there's a problem while streaming
                # we can only show one at a time, so pick the worst problem
                if bad_latency and bad_loss:
                    inapp_banner("Unstable connection", "Can you move to get better signal?", level)
                elif bad_latency:
                    inapp_banner("Unstable connection (Latency)", "Can you move to get better signal?", level)
                elif bad_loss:
                    inapp_banner("Unstable connection (Loss)", "Can you move to get better signal?", level)
                elif bad_cpu:
                    inapp_banner("High CPU", "Consider closing some apps or tabs", level)
                elif bad_memory:
                    inapp_banner("Low Memory", "Consider closing some apps or tabs", level)

            else:
                # just print the no streams onces
                if not no_streams_notified:
                    print("")
                    print("No streams active")
                no_streams_notified = True

        except speedify.SpeedifyError as sapie:
            print("SpeedifyError " + str(sapie))
        time.sleep(delay)

if __name__ == '__main__':
    main()
