import pandas as pd
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

# Things that could interfere with streams:
#  * High CPU - check
#  * High Memory - check
#  * Busy GPU - i only see code/clil for checking NVIDIA GPUs even though task manager shows it for any GPU
#  * Congestion - internet not fast enough for stream...  don't really see this in the cli output
#  * Loss of internet during stream
#  * Low Wifi signal strength
#  * Increase in packet loss?
#  * internet connections disconnecting?

# Issues:
#  * Notification is making a noise every time now.  I want silent notificaitons, the person is streaming!  fix https://stackoverflow.com/questions/56695061/is-there-any-way-to-disable-the-notification-sound-on-win10toast-python-library
#  * Not using the crossplatform notification library, would work on linux and mac if i did that
#  * There's a GPUUItl... but it only works on NVIDIA so i removed.
#  * Notifications show the app name as 'Python'.  It's true, and this is a prototype, so whatever.
#  * Wonder if there's a way to tell if there's  congestion that's causing stream to not hit full speed?

# If you don't see the notifications, it probably means you have Windows Focus Assist on.  Turn it off.

delay = 2 # sampling interval information

toaster = ToastNotifier()

low_memory = False
busy_cpus = 0
busy_cpus_now = False
is_streaming = False


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

def get_cpu_info():
    ''' :return:
         memtotal: Total Memory
         memfree: free memory
         memused: Linux: total - free, used memory
         mempercent: the proportion of memory used
         cpu: CPU usage of each accounting
    '''
    global low_memory
    global busy_cpus
    global busy_cpus_now

    mem = psutil.virtual_memory()
    memtotal = mem.total
    memfree = mem.free
    mempercent = mem.percent
    memused = mem.used
    # this cpu sometimes shoots off into the 90s but windows taskamanager doesn't show that.
    # strangely when this shows a high number and taskmanager doesn't my computer seems slow.
    # I think, strangely that this is more accurate. oh well, not digging further, it's a protoype

    cpu = psutil.cpu_percent(percpu=False)
    #print("Cpu: " + str(cpu))

    if mempercent > 95:
        if not low_memory:
            notify("Low Memory","Memory used: " + str(mempercent) + "%.  Can you close some apps or tabs?")
        low_memory = True
    else:
        low_memory = False

    #busy_cpus_now = 0
    total_cores = 0
    if cpu > 90:
            busy_cpus = busy_cpus + 1
    else:
        busy_cpus = 0
        busy_cpus_now = False
    if (busy_cpus > 1 and not busy_cpus_now):
        # notify after 2 in a row
        busy_cpus_now = True
        notify("CPU Busy", "CPU " + str(cpu ) + "% busy. Can you close some apps or tabs?")
    if (cpu < 40 and busy_cpus != busy_cpus_now):
        notify("CPUs Recovered", "CPU less busy")


    # meh, load is in a future release of psutil that pip doesn't have yet
    #load = psutil.getloadavg()
    #print("load: " + str(loads))
    return memtotal, memfree, memused, mempercent, cpu


 # Main function
def main():
    times = 0
    no_streams = True
    global is_streaming
    stream_name = None
    bad_latency = False
    bad_loss = False
    streams_problem = False
    current_state = "DISCONNECTED"
    current_streams = {}
    bad_internet_count =0
    bad_internet_notified = False
    while True:

                     # Prints the current time
        time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                     # Obtain information CPU

        try:
            stats = speedify.stats(1)

            active_streams = False
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
                    streams_problem = False
                    for stream in streams_array :
                        stream_id = stream["id"]
                        new_streams[stream_id] = stream
                        warning = ""
                        old_stream = None
                        if stream_id in current_streams:
                            old_stream = current_streams[stream_id]
                        else:
                            # new stream!  should we do anything special?
                            pass
                        if stream["active"] == True:
                            active_streams = True;
                            if "name" in stream:
                                # lazy cheat.  it's actually a list of streams, if there's more than one stream, i'm
                                # going to end out just using the name of the last
                                # active one which is not really correct, but i'm just
                                # experimenting, and most times there's just one.
                                app_name = stream["name"]
                            #print("active stream: " + str(stream))
                            uploadSpeed = stream["uploadSpeed"]
                            averageUploadSpeed = stream["averageUploadSpeed"]

                            # at this point I'm purposely biased towards uploadspeeds here
                            # and only use downloads in few places.  right or wrong?  unsute
                            downloadSpeed = stream["downloadSpeed"]
                            averageDownloadSpeed = stream["averageDownloadSpeed"]
                            print(str(app_name) + "     upload: " +str(uploadSpeed) + " avg upload: " + str(averageUploadSpeed))
                            slow_count = 0
                            if old_stream != None and "slow_count" in old_stream:
                                slow_count = old_stream["slow_count"]

                            if (uploadSpeed * 2) < averageUploadSpeed:
                                #print("slow stream")
                                # this could be two things:  slow or gone to 0.
                                # gone to 0 could be a disaster, or it might just be
                                # end of stream.
                                slow_count = slow_count+1
                                if slow_count > 2:
                                    warning = "slow"
                                    streams_problem = True
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
                                # stream has fallen to 0.  Hard or impossible to say if the
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

                            color = "[Green]"
                            if zero_count > 2:
                                # no data for 3 seconds?  Probably disconnected?
                                color = "[Grey]"
                            elif slow_count > 2 or zero_count > 1:
                                # below average for 3 seconds, or no data for 2?  probably having bad time
                                color = "[Yellow]"
                            print(color + " Streaming " + app_name + " " + warning)

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

            if not bad_internet_notified and bad_internet_count > 4:
                msg = ""
                if bad_loss :
                    msg = "Loss is high, "
                if bad_latency:
                    msg = msg+ "Latency is high, "
                notify("Unstable Connection", msg +" can you move to get better signal?")
                bad_internet_notified = True
            if(active_streams):
                no_streams = False
                # only notify about busy cpu / memory if we think you're live streaming.  otherwise it wouldn't be speedify's business
                (memtotal, memfree, memused, mempercent, cpu) = get_cpu_info()
                print ("")

                print ("|   CPU:    | " + str(cpu) + "% |")
                print ("|   Memory: | " + str(mempercent) + "% |")

                if cpu > 90:
                    print (" * High CPU.  Consider closing some apps or tabs")
                if mempercent > 95:
                    print (" * High memory usage.  Consider closing some apps or tabs")
                if bad_latency:
                    print (" * Unstable connection.  Latency is high, can you move to get better signal?")
                if bad_loss:
                    print (" * Unstable connection.  Loss is high, can you move to get better signal?")
                #if slow_count > 2:
                #    print (" * Stream slowed! ")
            else:
                # just print the no streams onces
                if not no_streams:
                    print("")
                    print("No streams active")
                no_streams = True

        except speedify.SpeedifyError as sapie:
            print("SpeedifyError " + str(sapie))
        time.sleep(delay)
        times += 1



if __name__ == '__main__':
    main()
