import sys

sys.path.append("../")
import speedify
from speedify import State
import time
import math
import json
import logging

# what properties do we want to test:
possible_attributes = ["jumbo", "transport", "encryption", "privacy_killswitch", "mode"]

"""
find and apply the best set of speedify settings for you, by trying
every possible combination, and test speed on each and every combo.

The settings in possible attributes are available to be tested by passing the
setting through the command line
ex: python measure_speeds.py jumbo transport
"""

logging.basicConfig(
    handlers=[logging.FileHandler("test.log"), logging.StreamHandler(sys.stdout)],
    format="%(asctime)s\t%(levelname)s\t%(module)s\t%(message)s",
    level=logging.DEBUG,
)


def apply_value(name, value):
    if name == "transport":
        transport = "tcp" if value else "udp"
        speedify.transport(transport)
    elif name == "mode":
        mode = "redundant" if value else "speed"
        speedify.mode(mode)
    elif name == "jumbo":
        speedify.jumbo(value)
    elif name == "encryption":
        speedify.encryption(value)
    elif name == "privacy_killswitch":
        speedify.killswitch(value)


def print_all_attr(attrlist, attrvalues):
    # should turn into json and dump
    settingsmap = {}
    for att, value in zip(attrlist, attrvalues):
        if str(att) == "transport":
            attval = "tcp" if value else "udp"
        elif str(att) == "redundant":
            attval = "redundant" if value else "speed"
        else:
            attval = value
        settingsmap[att] = attval
    logging.info(json.dumps(settingsmap))


def print_attr(attribute, value):
    if str(attribute) == "transport":
        attval = "tcp" if value else "udp"
    elif str(attribute) == "redundant":
        attval = "redundant" if value else "speed"
    else:
        attval = value
    logging.info(str(attribute) + " = " + str(attval))


def set_all_attr(attrlist, attrvalues):
    for att, value in zip(attrlist, attrvalues):
        apply_value(att, value)


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1000.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1000.0
    return "%.1f%s%s" % (num, "Yi", suffix)


def main():
    if len(sys.argv) > 1:
        # arguments specified on command line
        attributes = []
        for arg in sys.argv:
            if arg in possible_attributes:
                attributes.append(arg)
    else:
        logging.info("Need to pass in list of attributes to test")
        logging.info("Possible attributes: " + str(possible_attributes))
        sys.exit(1)

    logging.info("Testing with attributes: " + str(attributes))

    rounds = math.pow(2, len(attributes))

    # find the fastest server
    connect = speedify.connect_closest()
    # pull its name so we can connect directly from now on and no risk Getting
    # a different server
    server = connect["tag"]

    logging.info("Testing using server: " + server)

    # best results yet
    best_download = -1
    best_download_attributes = []
    best_upload = -1
    best_upload_attributes = []
    failed = False

    i = 0
    logging.info("== START ==")
    while i < rounds:
        logging.info("Loop: " + str(i))
        attributecount = 0
        atval = False
        # list of True|Falses same length as the list of attributes to be tested
        current_attributes = []
        # builds a logical table, first attribute alternates, second switches every
        # two, third attribute, every 4, so that every possible combination gets tried and tested
        for x in attributes:
            attributecount = attributecount + 1
            demonin = math.pow(2, attributecount)
            atval = True if i % demonin < (demonin / 2) else False
            current_attributes.append(atval)
        set_all_attr(attributes, current_attributes)
        print_all_attr(attributes, current_attributes)
        i = i + 1
        speedify.connect(server)
        state = speedify.show_state()
        if state != State.CONNECTED:
            time.time()
            logging.error("Did not connect!")
            failed = True
            break
        trcattempts = 0
        trc = False
        while trcattempts < 30:
            # lets make sure internet is working before proceeding
            # typically takes a dozen times through this loop before
            # we start seeing it really work.  think that's just windows.
            try:
                if speedify.using_speedify():
                    trc = True
                    break
            except FileNotFoundError:
                sys.exit(1)
            trcattempts = trcattempts + 1
            # internet can take a bit, give it some time
            time.sleep(0.2)
        if not trc:
            logging.warning("Speedify not providing internet!")
            continue
        speedresult = speedify.speedtest()
        if speedresult["status"] != "complete":
            logging.warning("Speedtest did not complete!")
        else:
            for result in speedresult["connectionResults"]:
                if result["adapterID"] == "speedify":
                    down = int(result["downloadBps"])
                    up = int(result["uploadBps"])

            logging.info("download speed - " + str(sizeof_fmt(down)) + "bps")
            if down > best_download:
                logging.info(" best download yet!")
                best_download = down
                best_download_attributes = list(current_attributes)
            logging.info("upload speed - " + str(sizeof_fmt(up)) + "bps")
            if up > best_upload:
                logging.info(" best upload yet!")
                best_upload = up
                best_upload_attributes = list(current_attributes)
        speedify.disconnect()

    if not failed:
        logging.info("== DONE ==")
        logging.info("best download : " + str(sizeof_fmt(best_download)) + "bps")
        print_all_attr(attributes, best_download_attributes)
        logging.info("best upload   : " + str(sizeof_fmt(best_upload)) + "bps")
        print_all_attr(attributes, best_upload_attributes)

        logging.info("Applying best download values")
        set_all_attr(attributes, best_download_attributes)
    else:
        logging.error("== FAILED ==")
        sys.exit(1)


if __name__ == "__main__":
    main()
