import sys
sys.path.append('../')
import speedify
import json
import os
import time

from speedify import Priority
from speedify import SpeedifyError
import logging

# Write out the current speedify settings to std out
# In format suitable for use with the Speedify for Teams API.
# if the first command line argument is "lock" then all the settings will be generated marked as locked

logging.basicConfig(handlers=[logging.FileHandler('test.log'),logging.StreamHandler(sys.stdout)],format='%(asctime)s\t%(levelname)s\t%(module)s\t%(message)s',  level=logging.INFO)

loops = 10

logging.info("START")
server_name = "us-nyc-18"
total = 0
count = 0
for x in range(1,loops):
    try:
        state = speedify.show_state();
        #logging.info("state at top of loop " + str(x) + " " + str(state))
        #time.sleep(2)
        start_time = time.time()

        connected_server = speedify.connect(server_name)
        if (connected_server["tag"] == server_name):
            elapsed_time = time.time() - start_time
            total = total + elapsed_time
            count = count + 1
            logging.info("connect took " + str(elapsed_time))
        else:
            logging.warning("connected to wrong server: " + str(connected_server["tag"]))
        time.sleep(2)
        #state = speedify.show_state();
        #time.sleep(2)
        speedify.disconnect()
        #time.sleep(2)
    except Exception as e:
        logging.warning("Loop " + str(x) + " Exception: " + str(e))

logging.info("DONE")
if count > 0:
    logging.info("Average connect time: " + str(total/count))
