import sys
sys.path.append('../')
import speedify
import json
import os

from speedify import Priority
from speedify import SpeedifyError
import logging

# Write out the current speedify settings to std out
# In format suitable for use with the Speedify for Teams API.
# if the first command line argument is "lock" then all the settings will be generated marked as locked

logging.basicConfig(handlers=[logging.FileHandler('test.log'),logging.StreamHandler(sys.stdout)],format='%(asctime)s\t%(levelname)s\t%(module)s\t%(message)s',  level=logging.INFO)

loops = 100

logging.info("START")

for x in range(1,loops):
    try:
        state = speedify.show_state();
        #logging.info("state at top of loop " + str(x) + " " + str(state))
        speedify.connect()
        state = speedify.show_state();
        speedify.disconnect()
    except Exception as e:
        logging.warning("Loop " + str(x) + " Exception: " + str(e))

logging.info("DONE")
