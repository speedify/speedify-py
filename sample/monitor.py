import pandas as pd
import GPUtil
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

# Issues:
#  * Notification is making a noise every time now.  I want silent notificaitons, the person is streaming!  fix https://stackoverflow.com/questions/56695061/is-there-any-way-to-disable-the-notification-sound-on-win10toast-python-library
#  * Not using the crossplatform notification library, would work on linux and mac if i did that
#  * GPU api turns out to be NVIDIA only, I'll probably tear that out at some point.
#  * Notifications show the app name as 'Python'.  It's true, and this is a prototype, so whatever.
#  * Wonder if there's a way to tell if there's  congestion that's causing stream to not hit full speed?

stopped_num = 10000000 # (set a maximum number of acquisition, to prevent explosions recorded text)
delay = 10 # sampling interval information
Gpus = GPUtil.getGPUs()
toaster = ToastNotifier()

low_memory = False
busy_cpus = 0
is_streaming = False


def get_gpu_info():
    '''
    :return:
    '''
    # only works on NVIDIA GPUS

    gpulist = []
    GPUtil.showUtilization()
    for k, gpu in Gpus:
        print('gpu.id:', gpu.id)
        print ( 'total GPU:', gpu.memoryTotal)
        print ( 'GPU usage:', gpu.memoryUsed)
        print ( 'gpu use proportion:', gpu.memoryUtil * 100)
        Press # to add information one by one GPU
        gpulist.append([ gpu.id, gpu.memoryTotal, gpu.memoryUsed,gpu.memoryUtil * 100])

    return gpulist


def get_cpu_info():
    ''' :return:
         memtotal: Total Memory
         memfree: free memory
         memused: Linux: total - free, used memory
         mempercent: the proportion of memory used
         cpu: CPU usage of each accounting
    '''
    global low_memory
    global toaster
    global busy_cpus
    mem = psutil.virtual_memory()
    memtotal = mem.total
    memfree = mem.free
    mempercent = mem.percent
    memused = mem.used
    cpu = psutil.cpu_percent(percpu=True)

    if mempercent > 90:
        if not low_memory:
            toaster.show_toast("Low Memory","Memory used: " + str(mempercent) + "%.  Can you close some apps or tabs?",icon_path="SpeedifyApp.ico")
        low_memory = True
    else:
        low_memory = False

    busy_cpus_now = 0
    total_cores = 0
    for cpu_perc in cpu :
        total_cores = total_cores + 1
        if cpu_perc > 90:
            busy_cpus_now = busy_cpus_now + 1
    if (busy_cpus_now > 0 and busy_cpus != busy_cpus_now):
        toaster.show_toast("CPUs Busy", str(busy_cpus_now) + " / " + str(total_cores) + " CPU Cores busy. Can you close some apps or tabs?",icon_path="SpeedifyApp.ico")
    if (busy_cpus_now == 0 and busy_cpus != busy_cpus_now):
        toaster.show_toast("CPUs Recovered", "No CPU Cores fully loaded",icon_path="SpeedifyApp.ico")
    busy_cpus = busy_cpus_now

    # meh, load is in a future release that pip doesn't have yet
    #load = psutil.getloadavg()
    #print("load: " + str(loads))
    return memtotal, memfree, memused, mempercent, cpu


 # Main function
def main():
    times = 0
    global is_streaming
    global toaster

    last_state = "DISCONNECTED"
    while True:
                 # The maximum number of cycles
        if times < stopped_num:
                         # Prints the current time
            time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                         # Obtain information CPU
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
                    for stream in streams_array :
                        if stream["active"] == True:
                            active_streams = True;
                            print("active stream")
                            streaming_right_now = True
                    if( streaming_right_now and not is_streaming):
                        toaster.show_toast("Live Stream","Speedify is enhancing streaming",icon_path="SpeedifyApp.ico" )
                    if( not streaming_right_now and is_streaming ):
                        toaster.show_toast("Stream Complete","Stream complete",icon_path="SpeedifyApp.ico" )
                    is_streaming = streaming_right_now
                if(str(json_array[0]) == "state"):
                    state_obj = json_array[1]
                    new_state = state_obj["state"]
                    if (new_state == "DISCONNECTED" or new_state == "DISCONNECTING") and is_streaming == True:
                        # stats returns things in whatever order it wants so there's no guarantee this will happen in this order to get caught
                        toaster.show_toast("Stream broke?!" , "Speedify disconnected during live stream",icon_path="SpeedifyApp.ico")
                        is_streaming = False
                    if new_state != last_state and new_state == "CONNECTED":
                        toaster.show_toast("Speedify Connected" , "Ready to start streaming",icon_path="SpeedifyApp.ico")
                        last_state = new_state
                    if (new_state == "DISCONNECTED" or new_state == "LOGGED_OUT") and (last_state != "LOGGED_OUT" and last_state != "LOGGED_IN" and last_state != "LOGGING_IN") :
                        toaster.show_toast("Speedify Disconnected" , "Connect before streaming",icon_path="SpeedifyApp.ico")

                    last_state = new_state
            if(active_streams):
                cpu_info = get_cpu_info()
                             # Obtain information GPU
                gpu_info = get_gpu_info()
                             # Added gap
                print(cpu_info)
                print(gpu_info,'\n')
            time.sleep(delay)
            times += 1
        else:
            break


if __name__ == '__main__':
    main()
