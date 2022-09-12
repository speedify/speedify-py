import sys

sys.path.append("../")
import speedify
from speedify import State, SpeedifyError, Priority

"""
This sample connects to the closest server and configures some speedify settings
"""

if len(sys.argv) > 2:
    user = sys.argv[1]
    password = sys.argv[2]

state = speedify.show_state()
print("Speedify's state is " + str(state))
if state == State.LOGGED_OUT:
    try:
        speedify.login(user, password)
    except Exception:
        print("Error could not login!")
        sys.exit(1)

try:
    if speedify.show_state() != State.LOGGED_IN:
        # get to LOGGED_IN state
        speedify.disconnect()
    state = speedify.show_state()
    print("Speedify's state is " + str(state))
except SpeedifyError:
    pass

try:
    print("Configuring settings")
    # make sure encryption is on
    speedify.encryption(True)
    # we do not want to connect everytime we login, just when we say
    speedify.startupconnect(False)
    # make our default connect(), connect to the closest server.
    speedify.connectmethod("closest")
    print("Settings configured")
except SpeedifyError as se:
    print("Error setting settings " + se.message)
    sys.exit(1)


try:
    print("connecting to the closest server")
    serverInfo = speedify.connect_closest()
    print("Server country: " + serverInfo["country"])
    print("Server city: " + serverInfo["city"])
    print("Server num: " + str(serverInfo["num"]))
    print("connected!")

    adapters = speedify.show_adapters()
    for adapter in adapters:
        if adapter["type"] == "Wi-Fi":
            print("Found a Wi-Fi card: " + str(adapter["description"]))
            guid = adapter["adapterID"]
            print("adapterID: " + str(guid))
            newadapters = speedify.adapter_priority(guid, Priority.ALWAYS)
            print("Priority: " + adapter["priority"])

    sys.exit(0)
except SpeedifyError as se:
    print("problems connecting " + se.message)
    sys.exit(1)
