import time
import psutil
import sys
from win10toast import ToastNotifier
# cross platform notifier... not using now
# from notifypy import Notify
sys.path.append('../')
import speedify
from speedify import State, SpeedifyError, Priority

# This program uses the speedify_cli to watch speedify for state and live streaming
# and then uses the psutil package to watch for excessive load that might interfere
# with steaming and shows hte users appropriate notifications.

# The Notification code is Windows only.  Everything else should work on macOS
# or Linux.  (but i haven't tried)

# We decide how a stream is doing by comparing its current upload/download to
# its average.  Falls generally mean an issue.  We how we think it's doing
# to change the color of the icon next to the stream: Green,Yellow,Red or Grey.

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

# Issues:
#  * Notification is making a noise every time now.  I want silent notificaitons, the person is streaming!  fix https://stackoverflow.com/questions/56695061/is-there-any-way-to-disable-the-notification-sound-on-win10toast-python-library
#  * Not using the crossplatform notification library, would work on linux and mac if i did that
#  * There's a GPUUItl... but it only works on NVIDIA so i removed.
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

# gets CPU and memory
def get_cpu_info():
    ''' :return:
         memtotal: Total Memory
         memfree: free memory
         memused: Linux: total - free, used memory
         mempercent: the proportion of memory used
         cpu: CPU usage of each accounting
    '''

    mem = psutil.virtual_memory()

    mempercent = mem.percent
    # this cpu sometimes shoots off into the 90s but windows taskamanager doesn't show that.
    # strangely when this shows a high number and taskmanager doesn't my computer seems slow.
    # I think, strangely that this is more accurate. oh well, not digging further, it's a protoype
    cpu = psutil.cpu_percent(percpu=False)
    #print("Cpu: " + str(cpu))



    # meh, load is in a future release of psutil that pip doesn't have yet
    #load = psutil.getloadavg()
    #print("load: " + str(loads))
    return mempercent, cpu


 # Main function
def main():
    no_streams = True
    is_streaming = False
    stream_name = None
    bad_latency = False
    bad_loss = False
    current_state = "DISCONNECTED"
    current_streams = {}
    bad_internet_count =0
    bad_internet_notified = False
    problems_yellow = False
    problems_red = False
    problems_grey = False
    low_memory_notified = False
    busy_cpus = 0
    busy_cpus_notified = False
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
                    #print("  IS streaming_stats")
                    #print("Item: " + str(json_array))

                    json_dict = json_array[1]
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
                            if "name" in stream:
                                app_name = stream["name"]

                            uploadSpeed = stream["uploadSpeed"]
                            averageUploadSpeed = stream["averageUploadSpeed"]


                            downloadSpeed = stream["downloadSpeed"]
                            averageDownloadSpeed = stream["averageDownloadSpeed"]
                            print("     " + str(app_name) + " upload: " +str(uploadSpeed) + " avg upload: " + str(averageUploadSpeed))
                            print("     " + str(app_name) + " download: " +str(uploadSpeed) + " avg download: " + str(averageUploadSpeed))
                            slow_count = 0
                            if old_stream != None and "slow_count" in old_stream:
                                slow_count = old_stream["slow_count"]

                            # we look at the average upload and download speeds for a stream
                            # to decide which one its doing more of, and assume that's the
                            # important direction.
                            mostly_upload = averageUploadSpeed > averageDownloadSpeed
                            print ("     mostly upload: " + str(mostly_upload) )
                            if ((uploadSpeed * 2) < averageUploadSpeed) if mostly_upload else ((downloadSpeed * 2) < averageDownloadSpeed):
                                # the speed in the "important direction" has dropped
                                # to less than 1/2 of what it was.  Suggestions a problem.
                                # this could be two things:  slow or gone to 0.
                                # gone to 0 could be a disaster, or it might just be
                                # end of stream.
                                slow_count = slow_count+1
                                if slow_count > 2:
                                    warning = "slow"
                                    slow_count = 3
                            else:
                                slow_count = slow_count -1
                                if slow_count < 0:
                                    slow_count = 0
                            stream["slow_count"] =slow_count

                            zero_count = 0
                            if old_stream != None and "zero_count" in old_stream:
                                zero_count = old_stream["zero_count"]
                            if uploadSpeed == 0 and downloadSpeed == 0:
                                # stream has fallen to 0 in both directions.  Hard or impossible to say if the
                                # stream ended or is totally busted.  Suspect that if we
                                # knew it was TCP then that would imply more likely a problem,
                                # and with UDP it's more likely just the stream deciding to end.

                                zero_count = zero_count + 1
                                if zero_count > 1:
                                    warning = "stopped"
                            else:
                                 zero_count = 0
                            stream["zero_count"] = zero_count

                            streaming_right_now = True

                            # Based on what we know, classify to a color.
                            # Green - all is well, we're streaming!
                            color = "Green"
                            if zero_count > 2:
                                # no data for 3 seconds?  Probably disconnected?
                                color = "Grey"
                                problems_grey = True
                            elif slow_count > 2 or zero_count > 1:
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
                        bad_latency = False
                        bad_loss = False
                        slow_count = 0
                    current_streams = new_streams
                if(str(json_array[0]) == "state"):
                    state_obj = json_array[1]
                    new_state = state_obj["state"]
                    if new_state!="CONNECTED":
                        # disconnected, reset all the stats
                        is_streaming = False
                        bad_latency = False
                        slow_count=0
                        bad_loss = False
                        bad_internet_count =0
                        bad_internet_notified = False
                    current_state = new_state
                if(str(json_array[0]) == "connection_stats"):
                    json_dict = json_array[1]
                    bad_latency_now = False
                    bad_loss_now = False
                    if is_streaming:
                        connections_array = json_dict["connections"]
                        for connection in connections_array:
                            #print(str(connection))
                            # works pretty well in that when internet is good no notifications, when it's
                            # terrible, I get a notification.  too many if i stand there though.
                            if "connected" in connection and "inFlight" in connection and "latencyMs" in connection:
                                if connection["connected"] == True and connection["inFlight"] > 0:
                                    if connection["latencyMs"] > 300:
                                        # we're actually using a connection with 250 ms latency!
                                        if not bad_latency:
                                            #notify("Unstable Connection", "Latency is high (" + str(connection["latencyMs"]) + "ms), can you move to get better signal?")
                                            bad_latency_now = True
                                            bad_internet_count = bad_internet_count + 1
                                    # loss is always 0????
                                    #print("loss send: " + str(connection["lossSend"]))
                                    #print("loss rx: " + str(connection["lossReceive"]))
                                    if (connection["lossReceive"] +connection["lossSend"]) > 0.03 and is_streaming:
                                        if not bad_loss:
                                            #notify("Unstable Connection", "Loss is high, can you move to get better signal?")
                                            bad_loss_now = True
                                            bad_internet_count = bad_internet_count + 1
                            bad_loss = bad_loss_now
                            bad_latency = bad_latency_now
                            if not bad_loss and not bad_latency:
                                bad_internet_count = bad_internet_count -1
                                if bad_internet_count < 0:
                                    bad_internet_count = 0

            if not bad_internet_notified and bad_internet_count > 3:
                msg = ""
                if bad_loss :
                    msg = "Loss is high, "
                if bad_latency:
                    msg = msg+ "Latency is high, "
                notify("Unstable Connection", msg +" can you move to get better signal?")
                bad_internet_notified = True
            if(is_streaming):
                # only notify about busy cpu / memory if we think you're live streaming.  otherwise it wouldn't be speedify's business
                no_streams = False
                (mempercent, cpu) = get_cpu_info()
                print ("")
                # think this should be shown in our ui when someone is streaming
                print ("|   CPU: " + str(cpu) + "% ,  Memory: " + str(mempercent) + "% |")
                if mempercent > 95:
                    if not low_memory_notified:
                        notify("Low Memory","Memory used: " + str(mempercent) + "%.  Can you close some apps or tabs?")
                    low_memory_notified = True
                else:
                    low_memory_notified = False


                # notification on CPU while streaming
                # should this only be done while there are problems?
                if cpu > 90:
                        busy_cpus = busy_cpus + 1
                else:
                    busy_cpus = 0
                if (busy_cpus > 1 and not busy_cpus_notified):
                    # notify after 2 in a row
                    busy_cpus_notified = True
                    notify("CPU Busy", "CPU " + str(cpu ) + "% busy. Can you close some apps or tabs?")
                if (cpu < 40 and busy_cpus_notified):
                    notify("CPUs Recovered", "CPU less busy")
                    busy_cpus_notified = False

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
                elif cpu > 90:
                    inapp_banner("High CPU", "Consider closing some apps or tabs", level)
                elif mempercent > 95:
                    inapp_banner("Low Memory", "Consider closing some apps or tabs", level)

            else:
                # just print the no streams onces
                if not no_streams:
                    print("")
                    print("No streams active")
                no_streams = True

        except speedify.SpeedifyError as sapie:
            print("SpeedifyError " + str(sapie))
        time.sleep(delay)

if __name__ == '__main__':
    main()
